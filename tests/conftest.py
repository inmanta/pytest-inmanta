"""
Copyright 2018 Inmanta

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

import glob
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterator, Optional

import pytest

import pytest_inmanta.plugin
from inmanta import env, loader, plugins
from inmanta.loader import PluginModuleFinder
from libpip2pi.commands import dir2pi

# be careful not to import any core>=6 objects directly
from pytest_inmanta.core import SUPPORTS_MODULES_V2

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def set_cwd(testdir):
    pytest_inmanta.plugin.CURDIR = os.getcwd()


@pytest.fixture(scope="function", autouse=True)
def reset_pytest_inmanta_state():
    yield
    pytest_inmanta.plugin.ProjectLoader.reset()


@pytest.fixture(scope="function", autouse=True)
def deactive_venv():
    old_os_path = os.environ.get("PATH", "")
    old_prefix = sys.prefix
    old_path = sys.path
    old_meta_path = sys.meta_path.copy()
    old_path_hooks = sys.path_hooks.copy()
    old_pythonpath = os.environ.get("PYTHONPATH", None)
    old_os_venv: Optional[str] = os.environ.get("VIRTUAL_ENV", None)

    yield

    os.environ["PATH"] = old_os_path
    sys.prefix = old_prefix
    sys.path = old_path
    # reset sys.meta_path because it might contain finders for editable installs, make sure to keep the same object
    sys.meta_path.clear()
    sys.meta_path.extend(old_meta_path)
    sys.path_hooks.clear()
    sys.path_hooks.extend(old_path_hooks)
    # Clear cache for sys.path_hooks
    sys.path_importer_cache.clear()
    # Restore PYTHONPATH
    if old_pythonpath is not None:
        os.environ["PYTHONPATH"] = old_pythonpath
    elif "PYTHONPATH" in os.environ:
        del os.environ["PYTHONPATH"]
    # Restore VIRTUAL_ENV
    if old_os_venv is not None:
        os.environ["VIRTUAL_ENV"] = old_os_venv
    elif "VIRTUAL_ENV" in os.environ:
        del os.environ["VIRTUAL_ENV"]
    # stay compatible with older versions of core: don't call the function if it doesn't exist
    if hasattr(env, "mock_process_env"):
        env.mock_process_env(python_path=sys.executable)
    if hasattr(PluginModuleFinder, "reset"):
        PluginModuleFinder.reset()
    plugins.PluginMeta.clear()
    loader.unload_inmanta_plugins()


@pytest.fixture
def examples_working_dir(pytestconfig) -> Iterator[None]:
    examples_dir: Path = pytestconfig.rootpath / "examples"
    current_dir: str = os.getcwd()
    os.chdir(examples_dir)
    yield
    os.chdir(current_dir)


@pytest.fixture(scope="session")
def examples_v2_package_index(pytestconfig) -> Iterator[str]:
    """
    Creates a local pip index for all v2 modules in the examples dir. The modules are built and published to the index.

    :return: The path to the index
    """
    if not SUPPORTS_MODULES_V2:
        pytest.skip(
            "Skipping modules v2 related tests for inmanta-core<6 (pre modules v2).",
        )

    examples_dir: Path = pytestconfig.rootpath / "examples"

    with tempfile.TemporaryDirectory() as artifact_dir:
        for module_dir in glob.iglob(str(examples_dir / "inmanta-module-*")):
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "inmanta.app",
                    "module",
                    "build",
                    "--output-dir",
                    artifact_dir,
                ],
                cwd=str(module_dir),
            )
        dir2pi(argv=["dir2pi", artifact_dir])
        yield os.path.join(artifact_dir, "simple")
