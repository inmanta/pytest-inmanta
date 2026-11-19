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
"""

import importlib
import importlib.metadata
import os
import pathlib
import shutil
import subprocess
import sys
import typing

import pytest

from inmanta import env
from pytest_inmanta import dynamic_modules


@pytest.fixture
def installer(
    monkeypatch: pytest.MonkeyPatch,
) -> typing.Iterator[dynamic_modules.FakeEditableInstaller]:
    """
    A fresh installer whose changes to sys.path and sys.modules are undone after the test.
    """
    monkeypatch.setattr(sys, "path", list(sys.path))
    modules_before = set(sys.modules)
    installer = dynamic_modules.FakeEditableInstaller()
    yield installer
    installer.cleanup()
    for name in set(sys.modules) - modules_before:
        if name.startswith("inmanta_plugins."):
            del sys.modules[name]
    importlib.invalidate_caches()


@pytest.fixture
def env_path(tmp_path: pathlib.Path) -> str:
    """
    A directory laid out like a venv, as far as the installer is concerned.
    """
    path = tmp_path / "venv"
    os.makedirs(env.PythonEnvironment.get_site_dir_for_env_path(str(path)))
    return str(path)


def create(
    installer: dynamic_modules.FakeEditableInstaller,
    env_path: str,
    project_dir: pathlib.Path,
    name: str,
) -> pathlib.Path:
    module_dir = project_dir / "libs" / name
    module_dir.parent.mkdir(parents=True, exist_ok=True)
    dynamic_modules.write_module(str(module_dir), name, "", "X = 1")
    installer.install(env_path, name, str(module_dir))
    return module_dir


def is_installed(name: str) -> bool:
    importlib.invalidate_caches()
    try:
        importlib.metadata.distribution(f"inmanta-module-{name}")
    except importlib.metadata.PackageNotFoundError:
        return False
    return True


def is_importable(name: str) -> bool:
    importlib.invalidate_caches()
    sys.modules.pop(f"inmanta_plugins.{name}", None)
    try:
        importlib.import_module(f"inmanta_plugins.{name}")
    except ImportError:
        return False
    return True


def test_install_and_cleanup(installer, env_path, tmp_path) -> None:
    """
    A dynamic module is importable and installed until the cleanup, which leaves nothing in the venv.
    """
    installer.use_project(str(tmp_path / "project"))
    create(installer, env_path, tmp_path / "project", "dyninstall")
    assert is_importable("dyninstall")
    assert is_installed("dyninstall")

    installer.cleanup()
    assert not is_importable("dyninstall")
    assert not is_installed("dyninstall")
    assert os.listdir(env.PythonEnvironment.get_site_dir_for_env_path(env_path)) == []


def test_project_change_uninstalls_other_projects_modules(
    installer, env_path, tmp_path
) -> None:
    """
    Switching to another test project uninstalls the dynamic modules of the previous one.
    """
    project1 = tmp_path / "project1"
    installer.use_project(str(project1))
    create(installer, env_path, project1, "dynproject")
    assert is_importable("dynproject")

    project2 = tmp_path / "project2"
    installer.use_project(str(project2))
    # The previous project's tree is still on disk, but its module is no longer visible
    assert (project1 / "libs" / "dynproject").is_dir()
    assert not is_importable("dynproject")
    assert not is_installed("dynproject")

    # The same name can be created in the new project
    create(installer, env_path, project2, "dynproject")
    assert is_importable("dynproject")


def test_prune_uninstalls_removed_modules(installer, env_path, tmp_path) -> None:
    """
    A dynamic module whose source directory was removed is uninstalled by prune.
    """
    installer.use_project(str(tmp_path / "project"))
    module_dir = create(installer, env_path, tmp_path / "project", "dynprune")
    shutil.rmtree(module_dir)
    assert is_installed("dynprune")

    installer.prune()
    assert not is_installed("dynprune")


def test_module_of_live_process_is_not_taken_over(
    installer, env_path, tmp_path
) -> None:
    """
    A run refuses to replace a dynamic module that another live pytest-inmanta process installed in the same venv, and
    replaces it when that process is gone.
    """
    site_dir = env.PythonEnvironment.get_site_dir_for_env_path(env_path)
    other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        dist_info = pathlib.Path(site_dir) / "inmanta_module_dynshared-0.1.0.dist-info"
        dist_info.mkdir()
        (dist_info / "INSTALLER").write_text(f"pytest-inmanta {other.pid}\n")
        installer.use_project(str(tmp_path / "project"))
        with pytest.raises(
            Exception, match=f"another pytest-inmanta process \\(pid {other.pid}\\)"
        ):
            create(installer, env_path, tmp_path / "project", "dynshared")
    finally:
        other.kill()
        other.wait()

    shutil.rmtree(tmp_path / "project" / "libs" / "dynshared")
    create(installer, env_path, tmp_path / "project", "dynshared")
    assert (dist_info / "INSTALLER").read_text() == f"pytest-inmanta {os.getpid()}\n"


def test_module_of_other_installer_is_not_replaced(
    installer, env_path, tmp_path
) -> None:
    """
    A dynamic module can't take the name of a module installed by another tool.
    """
    site_dir = env.PythonEnvironment.get_site_dir_for_env_path(env_path)
    dist_info = pathlib.Path(site_dir) / "inmanta_module_dynreal-1.0.0.dist-info"
    dist_info.mkdir()
    (dist_info / "INSTALLER").write_text("pip\n")
    installer.use_project(str(tmp_path / "project"))
    with pytest.raises(
        Exception, match="can't share its name with an installed module"
    ):
        create(installer, env_path, tmp_path / "project", "dynreal")
    assert dist_info.is_dir()


def test_stale_pth_files_are_removed(installer, env_path, tmp_path) -> None:
    """
    The .pth file of a pytest-inmanta process that is no longer running is removed.
    """
    site_dir = pathlib.Path(env.PythonEnvironment.get_site_dir_for_env_path(env_path))
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    stale = site_dir / f"pytest-inmanta-modules-{dead.pid}.pth"
    stale.write_text("/does/not/exist\n")
    installer.use_project(str(tmp_path / "project"))
    create(installer, env_path, tmp_path / "project", "dynpth")
    assert not stale.exists()
