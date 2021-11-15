"""
    Copyright 2021 Inmanta

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
# Note: These tests only function when the pytest output is not modified by plugins such as pytest-sugar!

import importlib
import logging
import os
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Optional, Sequence

import pkg_resources
import pytest
from pkg_resources import DistributionNotFound

# be careful not to import any core>=6 objects directly
from inmanta import env
from packaging import version

CORE_VERSION: Optional[version.Version]
"""
Version of the inmanta-core package. None if it is not installed.
"""

try:
    CORE_VERSION = version.Version(
        pkg_resources.get_distribution("inmanta-core").version
    )
except DistributionNotFound:
    CORE_VERSION = None


if CORE_VERSION is None or CORE_VERSION < version.Version("6.dev"):
    pytest.skip(
        "Skipping modules v2 tests for inmanta-core<6 (pre modules v2).",
        allow_module_level=True,
    )


@pytest.fixture(scope="session")
def testmodulev2_venv(pytestconfig) -> env.VirtualEnv:
    """
    Yields a Python environment with testmodulev2 installed in it.
    """
    with tempfile.TemporaryDirectory() as venv_dir:
        # set up environment
        venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
        venv.init_env()
        # workaround for pypa/build#405: unset PYTHONPATH because it's not required in this case and it triggers a bug in build
        with open(os.path.join(venv.site_packages_dir, "sitecustomize.py"), "a") as fd:
            fd.write(
                """
import os

if "PYTHONPATH" in os.environ:
    del os.environ["PYTHONPATH"]
                """.strip()
            )
        # install test module into environment
        subprocess.check_call(
            [
                venv.python_path,
                "-m",
                "inmanta.app",
                "module",
                "install",
                str(pytestconfig.rootpath / "examples" / "testmodulev2"),
            ],
        )
        yield venv


@pytest.fixture(scope="function")
def testmodulev2_venv_active(deactive_venv, testmodulev2_venv) -> env.VirtualEnv:
    """
    Activates a Python environment with testmodulev2 installed in it for the currently running process.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a unique function-scoped venv dir to prevent caching issues with inmanta_plugins' submodule_search_locations
        unique_env_dir: str = os.path.join(tmpdir, ".env")
        os.symlink(testmodulev2_venv.env_path, unique_env_dir)
        print(unique_env_dir)
        unique_env: env.VirtualEnv = env.VirtualEnv(env_path=unique_env_dir)
        unique_env.use_virtual_env()
        yield unique_env
        unload_modules_for_path(unique_env.site_packages_dir)


def unload_modules_for_path(path: str) -> None:
    """
    Unload any modules that are loaded from a given path.
    """

    def module_in_prefix(module: ModuleType, prefix: str) -> bool:
        file: Optional[str] = getattr(module, "__file__", None)
        return file.startswith(prefix) if file is not None else False

    loaded_modules: Sequence[str] = [
        mod_name for mod_name, mod in sys.modules.items() if module_in_prefix(mod, path)
    ]
    for mod_name in loaded_modules:
        del sys.modules[mod_name]
    importlib.invalidate_caches()


def test_basic_example(testdir, caplog, testmodulev2_venv_active):
    """
    Make sure that our plugin works for v2 modules.
    """
    testdir.copy_example("testmodulev2")

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        result = testdir.runpytest_inprocess("tests/test_basics.py")
        result.assert_outcomes(passed=1)
        # The testmodulev2_venv_active fixture does not install the module in editable mode. For pytest-inmanta tests this is
        # fine but for module testing this is likely a mistake. Verify that the plugin raises an appropriate warning.
        assert (
            "The module being tested is not installed in editable mode."
            " As a result the tests will not pick up any changes to the local source files."
            " To install it in editable mode, run `inmanta module install -e .`."
            in caplog.messages
        )


def test_basic_example_no_install(testdir):
    """
    Make sure that the plugin reports an informative error if the module under test is not installed.
    """
    testdir.copy_example("testmodulev2")

    result = testdir.runpytest_inprocess("tests/test_basics.py::test_compile", "-s")

    result.assert_outcomes(errors=1)
    result.stdout.re_match_lines(
        [
            r".*Exception: The module being tested is not installed in the current Python environment\."
            r" Please install it with `inmanta module install -e \.` before running the tests\..*"
        ]
    )
