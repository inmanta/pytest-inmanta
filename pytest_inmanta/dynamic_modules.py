"""
Copyright 2026 Inmanta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact: code@inmanta.com

Dynamic test modules: V2 module trees written by the tests themselves, made visible to the compiler as editable modules
without installing them.

A finder at the front of ``sys.meta_path`` resolves ``inmanta_plugins.<name>`` to the plugin package of the module's tree,
``<source dir>/inmanta_plugins/<name>``. That is all core needs to load an editable V2 module: it takes the source root two
levels up from the package's ``__init__.py``, next to ``setup.cfg``, and reads the version from ``setup.cfg``. Nothing is
written into the venv, so there is nothing to clean up and test runs that share a venv don't see each other's modules.

A module is dropped when the test project changes or its source directory is removed.
"""

import importlib.abc
import importlib.machinery
import importlib.metadata
import importlib.util
import os
import pathlib
import shutil
import sys
import types
import typing
from collections import abc

from inmanta import const

DYNAMIC_MODULE_VERSION = "0.1.0"

SETUP_CFG = """\
[metadata]
name = inmanta-module-{name}
version = {version}
license = Test License

[options]
zip_safe = False
include_package_data = True
packages = find_namespace:
"""

PYPROJECT_TOML = """\
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
"""


def write_module(module_dir: str, name: str, initcf: str, initpy: str) -> None:
    """
    Write a V2 module tree for module `name` in `module_dir`, which must not exist yet.
    """
    root = pathlib.Path(module_dir)
    root.mkdir()
    for subdir in ("model", "files", "templates"):
        (root / subdir).mkdir()
    plugin_dir = root / "inmanta_plugins" / name
    plugin_dir.mkdir(parents=True)
    (root / "model" / "_init.cf").write_text(initcf)
    (plugin_dir / "__init__.py").write_text(initpy)
    (root / "setup.cfg").write_text(
        SETUP_CFG.format(name=name, version=DYNAMIC_MODULE_VERSION)
    )
    (root / "pyproject.toml").write_text(PYPROJECT_TOML)


def module_subdir(name: str, subdir: str) -> str:
    """
    Map a V1 module subdirectory to its place in a V2 module tree.
    """
    if subdir == "plugins":
        return os.path.join("inmanta_plugins", name)
    if subdir.startswith("plugins/"):
        return os.path.join("inmanta_plugins", name, subdir[len("plugins") + 1 :])
    return subdir


class DynamicModuleFinder(importlib.abc.MetaPathFinder):
    """
    Finds the plugin packages of dynamic modules.

    It only answers for the top-level package ``inmanta_plugins.<name>`` of a registered module. That package's
    ``__path__`` is its directory, so Python's own path finder handles its submodules.

    One instance serves the whole process. Registering a module again from the same source directory, as the project
    fixture does for the unittest module, changes nothing.
    """

    def __init__(self) -> None:
        self._project_dir: typing.Optional[str] = None
        # module name -> source dir
        self._sources: dict[str, str] = {}

    def _ensure_on_meta_path(self) -> None:
        # Something that restores sys.meta_path from a snapshot can drop this finder
        if self not in sys.meta_path:
            sys.meta_path.insert(0, self)

    def install(self, name: str, source_dir: str) -> None:
        """
        Make the V2 module tree at `source_dir` the source of module `name`.
        """
        source_dir = os.path.realpath(source_dir)
        previous: typing.Optional[str] = self._sources.get(name)
        if previous == source_dir:
            self._ensure_on_meta_path()
            return
        try:
            importlib.metadata.distribution(f"inmanta-module-{name.replace('_', '-')}")
        except importlib.metadata.PackageNotFoundError:
            pass
        else:
            raise Exception(
                f"Module {name} is already installed. A dynamic test module can't share its name with an installed module."
            )
        if previous is not None:
            # A rewritten file of the same size in the same second could be served from stale bytecode
            shutil.rmtree(
                os.path.join(source_dir, const.PLUGINS_PACKAGE, name, "__pycache__"),
                ignore_errors=True,
            )
        self._sources[name] = source_dir
        self._ensure_on_meta_path()

    def use_project(self, project_dir: str) -> None:
        """
        Make `project_dir` the current test project: drop every dynamic module whose source is outside of it.
        """
        project_dir = os.path.realpath(project_dir)
        if project_dir == self._project_dir:
            return
        self._project_dir = project_dir
        for name, source_dir in list(self._sources.items()):
            if not source_dir.startswith(project_dir + os.sep):
                del self._sources[name]

    def prune(self) -> None:
        """
        Drop every dynamic module whose source directory no longer exists.
        """
        for name, source_dir in list(self._sources.items()):
            if not os.path.isdir(source_dir):
                del self._sources[name]
        self._ensure_on_meta_path()

    def find_spec(
        self,
        fullname: str,
        path: typing.Optional[abc.Sequence[str]],
        target: typing.Optional[types.ModuleType] = None,
    ) -> typing.Optional[importlib.machinery.ModuleSpec]:
        prefix = f"{const.PLUGINS_PACKAGE}."
        if not fullname.startswith(prefix):
            return None
        name = fullname[len(prefix) :]
        source_dir: typing.Optional[str] = self._sources.get(name)
        if source_dir is None:
            return None
        package_dir = os.path.join(source_dir, const.PLUGINS_PACKAGE, name)
        init = os.path.join(package_dir, "__init__.py")
        if not os.path.isfile(init):
            return None
        # A standard spec: core treats a module whose package is loaded by its V1 loader as a V1 module
        return importlib.util.spec_from_file_location(
            fullname, init, submodule_search_locations=[package_dir]
        )


FINDER = DynamicModuleFinder()
