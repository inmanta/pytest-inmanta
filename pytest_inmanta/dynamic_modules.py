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

The trees live in the project's ``libs/`` directory, which is also where core looks for V1 modules. Core warns on every
compile that such a module is installed both as a V1 and a V2 module. That warning is dropped for dynamic modules.
"""

import importlib.abc
import importlib.machinery
import importlib.metadata
import importlib.util
import logging
import os
import pathlib
import shutil
import sys
import types
import typing
from collections import abc

from inmanta import const, module

DYNAMIC_MODULE_VERSION = "0.1.0"

# Logged by core's inmanta.module when a module is found both in libs/ and as an installed V2 module
V1_AND_V2_WARNING = (
    "Module %s is installed as a V1 module and a V2 module: V1 will be ignored."
)

SETUP_CFG = """\
[metadata]
name = {package_name}
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
    Write a V2 module tree with an empty files/ and templates/ directory.

    :param module_dir: The root directory of the tree. It must not exist yet, its parent must.
    :param name: The name of the module.
    :param initcf: The content of the module's model/_init.cf.
    :param initpy: The content of the module's plugin package, inmanta_plugins/<name>/__init__.py.
    :raises FileExistsError: `module_dir` already exists.
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
        SETUP_CFG.format(
            package_name=module.ModuleV2Source.get_package_name_for(name),
            version=DYNAMIC_MODULE_VERSION,
        )
    )
    (root / "pyproject.toml").write_text(PYPROJECT_TOML)


def module_subdir(name: str, subdir: str) -> str:
    """
    Map a V1 module subdirectory to its place in a V2 module tree.

    :param name: The name of the module.
    :param subdir: A subdirectory of a V1 module tree, relative to its root, with "/" as separator. For example "plugins",
        "plugins/sub" or "templates".
    :return: The same subdirectory in a V2 module tree, relative to its root. "plugins" maps to "inmanta_plugins/<name>";
        any other subdirectory is unchanged.
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

    One instance serves the whole process.
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
        Make the V2 module tree at `source_dir` the source of module `name`. Registering a module again from the same
        source directory changes nothing.

        :param name: The name of the module.
        :param source_dir: The root directory of the module's tree, as written by `write_module`.
        :raises Exception: A module with this name is installed in the venv.
        """
        source_dir = os.path.realpath(source_dir)
        if self._sources.get(name) != source_dir:
            try:
                importlib.metadata.distribution(
                    module.ModuleV2Source.get_package_name_for(name)
                )
            except importlib.metadata.PackageNotFoundError:
                pass
            else:
                raise Exception(
                    f"Module {name} is already installed. A dynamic test module can't share its name with an installed module."
                )
            self._sources[name] = source_dir
        self._ensure_on_meta_path()

    def use_project(self, project_dir: str) -> None:
        """
        Make `project_dir` the current test project: drop every dynamic module whose source is outside of it.

        :param project_dir: The root directory of the test project.
        """
        project_dir = os.path.realpath(project_dir)
        if project_dir == self._project_dir:
            return
        self._project_dir = project_dir
        for name, source_dir in list(self._sources.items()):
            if not source_dir.startswith(project_dir + os.sep):
                del self._sources[name]

    def is_dynamic(self, name: str) -> bool:
        """
        Whether a dynamic module is registered under this name.

        :param name: The name of a module.
        """
        return name in self._sources

    def prune(self) -> None:
        """
        Prepare the dynamic modules for a compile. Drop every dynamic module whose source directory no longer exists.

        Remove the bytecode of the other ones. Python reuses a module's bytecode when the source file has the same size
        and the same modification time in whole seconds, so a test that rewrites a plugin file would otherwise run the old
        code.
        """
        for name, source_dir in list(self._sources.items()):
            if not os.path.isdir(source_dir):
                del self._sources[name]
                continue
            for dirpath, dirnames, _ in os.walk(
                os.path.join(source_dir, const.PLUGINS_PACKAGE, name)
            ):
                if "__pycache__" in dirnames:
                    dirnames.remove("__pycache__")
                    shutil.rmtree(
                        os.path.join(dirpath, "__pycache__"), ignore_errors=True
                    )
        # Python caches directory listings: make sure plugin files added since the previous compile are found
        importlib.invalidate_caches()
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


class V1AndV2WarningFilter(logging.Filter):
    """
    Drops core's warning that a module is installed both as a V1 and a V2 module, when that module is a dynamic module.
    """

    def __init__(self, finder: DynamicModuleFinder) -> None:
        super().__init__()
        self._finder = finder

    def filter(self, record: logging.LogRecord) -> bool:
        if (
            record.msg != V1_AND_V2_WARNING
            or not isinstance(record.args, tuple)
            or len(record.args) != 1
        ):
            return True
        return not self._finder.is_dynamic(str(record.args[0]))


FINDER = DynamicModuleFinder()
logging.getLogger(module.__name__).addFilter(V1AndV2WarningFilter(FINDER))
