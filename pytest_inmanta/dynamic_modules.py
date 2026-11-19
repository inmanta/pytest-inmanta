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

Dynamic test modules: V2 module trees written by the tests themselves, made visible to the compiler as editable installs
without running pip.

A fake editable install writes the two things core looks at to find an editable V2 module:

* an install record, ``inmanta_module_<name>-<version>.dist-info``, in the venv's site-packages. ``importlib.metadata``
  reads the version from it, and its ``direct_url.json`` marks the install as editable.
* an import path for ``inmanta_plugins.<name>``: a symlink in a staging directory to the module's plugin package. One
  ``.pth`` file in site-packages puts the staging directory on ``sys.path``. Core resolves the symlink and finds the module's
  source root two levels up.

A module is uninstalled when the test project changes or its source directory is removed, and everything written into
the venv is removed when the process exits. A venv can't be shared by test runs that run at the same time: a run refuses
to take over a module that another live run installed.
"""

import atexit
import configparser
import dataclasses
import importlib
import json
import os
import pathlib
import shutil
import site
import sys
import tempfile
import typing

from inmanta import env

DYNAMIC_MODULE_VERSION = "0.1.0"
INSTALLER = "pytest-inmanta"
PTH_PREFIX = "pytest-inmanta-modules-"

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


@dataclasses.dataclass(frozen=True)
class FakeInstall:
    """
    One dynamic module installed by a FakeEditableInstaller.

    :param site_dir: The site-packages dir of the venv the module is installed in.
    :param source_dir: The root of the module's V2 tree.
    :param dist_info: The install record written for the module in site_dir.
    """

    site_dir: str
    source_dir: str
    dist_info: str


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # The process exists but belongs to another user
        return True
    return True


def _installer_pid(installer_file: pathlib.Path) -> typing.Optional[int]:
    """
    Return the PID of the pytest-inmanta process that wrote an install record, or None if pytest-inmanta didn't write it.
    """
    if not installer_file.exists():
        return None
    words = installer_file.read_text().split()
    if len(words) != 2 or words[0] != INSTALLER or not words[1].isdigit():
        return None
    return int(words[1])


class FakeEditableInstaller:
    """
    Installs dynamic modules in editable mode by writing the install record and the import path directly.

    One instance serves the whole process. It installs each module from a given source directory only once, so recreating
    a module tree at the same path, as the project fixture does for the unittest module, costs nothing.

    A module stays installed only while it belongs to the current test project: use_project drops the modules of another
    project, and prune drops the modules whose source directory is gone.
    """

    def __init__(self) -> None:
        self._staging_dir: typing.Optional[str] = None
        self._project_dir: typing.Optional[str] = None
        # module name -> install
        self._installs: dict[str, FakeInstall] = {}
        self._pth_files: set[str] = set()
        # A forked child inherits the exit hook, but the files belong to this process
        self._owner_pid: int = os.getpid()
        atexit.register(self.cleanup)

    def _get_staging_dir(self) -> str:
        if self._staging_dir is None:
            self._staging_dir = tempfile.mkdtemp(prefix="pytest-inmanta-modules-")
            os.mkdir(os.path.join(self._staging_dir, "inmanta_plugins"))
        return self._staging_dir

    def _link_path(self, name: str) -> str:
        return os.path.join(self._get_staging_dir(), "inmanta_plugins", name)

    def _ensure_import_path(self, site_dir: str) -> None:
        staging_dir = self._get_staging_dir()
        pth_file = os.path.join(site_dir, f"{PTH_PREFIX}{os.getpid()}.pth")
        if pth_file not in self._pth_files:
            self._remove_stale_pth_files(site_dir)
            with open(pth_file, "w") as fd:
                fd.write(staging_dir + "\n")
            self._pth_files.add(pth_file)
        # The .pth file is only read at interpreter startup or by addsitedir, so this process needs the entry itself.
        site.addsitedir(site_dir)
        if staging_dir not in sys.path:
            sys.path.append(staging_dir)

    def _remove_stale_pth_files(self, site_dir: str) -> None:
        """
        Remove the .pth files left in site_dir by pytest-inmanta processes that are no longer running.
        """
        for pth_file in pathlib.Path(site_dir).glob(f"{PTH_PREFIX}*.pth"):
            pid = pth_file.stem[len(PTH_PREFIX) :]
            if pid.isdigit() and not _pid_alive(int(pid)):
                pth_file.unlink(missing_ok=True)

    def use_project(self, project_dir: str) -> None:
        """
        Make `project_dir` the current test project: uninstall every dynamic module whose source is outside of it.
        """
        project_dir = os.path.realpath(project_dir)
        if project_dir == self._project_dir:
            return
        self._project_dir = project_dir
        for name, install in list(self._installs.items()):
            if not install.source_dir.startswith(project_dir + os.sep):
                self._uninstall(name)

    def prune(self) -> None:
        """
        Uninstall every dynamic module whose source directory no longer exists.
        """
        for name, install in list(self._installs.items()):
            if not os.path.isdir(install.source_dir):
                self._uninstall(name)

    def _uninstall(self, name: str) -> None:
        install = self._installs.pop(name)
        link = self._link_path(name)
        if os.path.lexists(link):
            os.unlink(link)
        shutil.rmtree(install.dist_info, ignore_errors=True)
        importlib.invalidate_caches()

    def install(self, env_path: str, name: str, source_dir: str) -> None:
        """
        Make the V2 module tree at `source_dir` the editable install of module `name` in the venv at `env_path`.
        """
        # With --venv, env_path is a symlink inside the project dir, which is removed before the cleanup runs
        site_dir = os.path.realpath(
            env.PythonEnvironment.get_site_dir_for_env_path(env_path)
        )
        source_dir = os.path.realpath(source_dir)
        previous: typing.Optional[FakeInstall] = self._installs.get(name)
        if previous is not None:
            if previous.site_dir == site_dir and previous.source_dir == source_dir:
                return
            self._uninstall(name)

        self._ensure_import_path(site_dir)

        plugin_dir = os.path.join(source_dir, "inmanta_plugins", name)
        link = self._link_path(name)
        if os.path.lexists(link):
            os.unlink(link)
        os.symlink(plugin_dir, link)
        if previous is not None:
            # A rewritten file of the same size in the same second could be served from stale bytecode
            shutil.rmtree(os.path.join(plugin_dir, "__pycache__"), ignore_errors=True)

        dist_info = self._write_dist_info(site_dir, name, source_dir)
        self._installs[name] = FakeInstall(
            site_dir=site_dir, source_dir=source_dir, dist_info=dist_info
        )
        importlib.invalidate_caches()

    def _write_dist_info(self, site_dir: str, name: str, source_dir: str) -> str:
        dist_name = f"inmanta_module_{name.replace('-', '_')}"
        for existing in pathlib.Path(site_dir).glob(f"{dist_name}-*.dist-info"):
            owner: typing.Optional[int] = _installer_pid(existing / "INSTALLER")
            if owner is None:
                raise Exception(
                    f"Module {name} is already installed in {site_dir}. "
                    "A dynamic test module can't share its name with an installed module."
                )
            if owner != os.getpid() and _pid_alive(owner):
                raise Exception(
                    f"Dynamic module {name} is in use in {site_dir} by another pytest-inmanta process (pid {owner}). "
                    "Test runs that run at the same time can't share a venv."
                )
            shutil.rmtree(existing)

        config = configparser.ConfigParser()
        config.read(os.path.join(source_dir, "setup.cfg"))
        version: str = config.get(
            "metadata", "version", fallback=DYNAMIC_MODULE_VERSION
        )
        requires: list[str] = [
            line.strip()
            for line in config.get(
                "options", "install_requires", fallback=""
            ).splitlines()
            if line.strip()
        ]

        dist_info = pathlib.Path(site_dir) / f"{dist_name}-{version}.dist-info"
        dist_info.mkdir()
        metadata = [
            "Metadata-Version: 2.1",
            f"Name: inmanta-module-{name.replace('_', '-')}",
            f"Version: {version}",
            *(f"Requires-Dist: {req}" for req in requires),
        ]
        files: dict[str, str] = {
            "METADATA": "\n".join(metadata) + "\n",
            "INSTALLER": f"{INSTALLER} {os.getpid()}\n",
            "direct_url.json": json.dumps(
                {
                    "url": pathlib.Path(source_dir).as_uri(),
                    "dir_info": {"editable": True},
                }
            ),
        }
        for file_name, content in files.items():
            (dist_info / file_name).write_text(content)
        record = [f"{dist_info.name}/{file_name},," for file_name in [*files, "RECORD"]]
        (dist_info / "RECORD").write_text("\n".join(record) + "\n")
        return str(dist_info)

    def cleanup(self) -> None:
        """
        Remove everything this installer wrote outside of the module source trees.
        """
        if os.getpid() != self._owner_pid:
            return
        for name in list(self._installs):
            self._uninstall(name)
        for path in self._pth_files:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
        if self._staging_dir is not None:
            shutil.rmtree(self._staging_dir, ignore_errors=True)
        self._pth_files.clear()
        self._staging_dir = None
        self._project_dir = None


INSTALLER_INSTANCE = FakeEditableInstaller()
