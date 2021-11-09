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

import pytest
import subprocess
import tempfile

from inmanta import env

# TODO: disable all tests in this file for core < modv2 (modulesv2 fixture?)


@pytest.fixture(scope="session")
def testmodulev2_venv(pytestconfig) -> env.VirtualEnv:
    # TODO: docstring
    with tempfile.TemporaryDirectory() as venv_dir:
        # set up environment
        venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
        venv.init_env()
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
def v2_env(deactive_venv, testmodulev2_venv) -> None:
    # TODO: docstring
    testmodulev2_venv.use_virtual_env()
    env.mock_process_env(python_path=testmodulev2_venv.python_path)
    yield


def test_basic_example(testdir, v2_env):
    """
    Make sure that our plugin works for v2 modules.
    """
    testdir.copy_example("testmodulev2")

    # TODO: also verify exception when v2_env is not used (module not installed)
    result = testdir.runpytest("tests/test_basics.py")

    result.assert_outcomes(passed=1)
