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
import logging
import os
import subprocess

# Note: These tests only function when the pytest output is not modified by plugins such as pytest-sugar!
import tempfile
from importlib.abc import Loader
from typing import Iterator, Optional, Tuple

import pytest

# be careful not to import any core>=6 objects directly
import core
import utils
from inmanta import env

if not core.SUPPORTS_MODULES_V2:
    pytest.skip(
        "Skipping modules v2 tests for inmanta-core<6 (pre modules v2).",
        allow_module_level=True,
    )


@pytest.fixture(scope="session")
def testmodulev2_venv(pytestconfig) -> Iterator[env.VirtualEnv]:
    """
    Yields a Python environment with testmodulev2 installed in it.
    """
    with tempfile.TemporaryDirectory() as venv_dir:
        # set up environment
        venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
        venv.init_env()
        venv_unset_python_path(venv)
        # install test module into environment
        subprocess.check_call(
            [
                venv.python_path,
                "-m",
                "inmanta.app",
                "-X",
                "module",
                "install",
                str(pytestconfig.rootpath / "examples" / "testmodulev2"),
            ],
        )
        yield venv


def venv_unset_python_path(venv: env.VirtualEnv) -> None:
    """
    Workaround for pypa/build#405: unset PYTHONPATH because it's not required in this case and it triggers a bug in build
    """
    sitecustomize_existing: Optional[
        Tuple[Optional[str], Loader]
    ] = env.ActiveEnv.get_module_file("sitecustomize")
    # inherit from existing sitecustomize.py
    sitecustomize_inherit: str
    if sitecustomize_existing is not None and sitecustomize_existing[0] is not None:
        with open(sitecustomize_existing[0], "r") as fd:
            sitecustomize_inherit = fd.read()
    else:
        sitecustomize_inherit = ""
    with open(os.path.join(venv.site_packages_dir, "sitecustomize.py"), "a") as fd:
        fd.write(
            f"""
{sitecustomize_inherit}

import os

if "PYTHONPATH" in os.environ:
    del os.environ["PYTHONPATH"]
            """.strip()
        )


@pytest.fixture(scope="function")
def testmodulev2_venv_active(
    deactive_venv, testmodulev2_venv
) -> Iterator[env.VirtualEnv]:
    """
    Activates a Python environment with testmodulev2 installed in it for the currently running process.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a unique function-scoped venv dir to prevent caching issues with inmanta_plugins' submodule_search_locations
        unique_env_dir: str = os.path.join(tmpdir, ".env")
        os.symlink(testmodulev2_venv.env_path, unique_env_dir)
        unique_env: env.VirtualEnv = env.VirtualEnv(env_path=unique_env_dir)
        unique_env.use_virtual_env()
        yield unique_env
        utils.unload_modules_for_path(unique_env.site_packages_dir)


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

    result = testdir.runpytest_inprocess("tests/test_basics.py::test_compile")

    result.assert_outcomes(errors=1)
    result.stdout.re_match_lines(
        [
            r".*Exception: The module being tested is not installed in the current Python environment\."
            r" Please install it with `inmanta module install -e \.` before running the tests\..*"
        ]
    )


def test_import(testdir, testmodulev2_venv_active):
    """
    Make sure that our plugin works for v2 modules.
    """
    testdir.copy_example("testmodulev2")

    result = testdir.runpytest_inprocess("tests/test_import.py")

    result.assert_outcomes(passed=3)
