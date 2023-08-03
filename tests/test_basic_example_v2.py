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

# Note: These tests only function when the pytest output is not modified by plugins such as pytest-sugar!
from typing import Iterator

import pytest

import utils
from inmanta import env

# be careful not to import any core>=6 objects directly
from pytest_inmanta.core import SUPPORTS_MODULES_V2

if not SUPPORTS_MODULES_V2:
    pytest.skip(
        "Skipping modules v2 tests for inmanta-core<6 (pre modules v2).",
        allow_module_level=True,
    )


@pytest.fixture(scope="function")
def testmodulev2_editable_install() -> bool:
    raise NotImplementedError(
        "Tests using the testmodulev2 should have a marker specifying whether the module "
        "should be installed in editable mode or not."
    )


@pytest.fixture(scope="function")
def testmodulev2_venv(
    testdir: pytest.Testdir,
    pytestconfig: pytest.Config,
    testmodulev2_editable_install: bool,
) -> Iterator[env.VirtualEnv]:
    """
    Yields a Python environment with testmodulev2 installed in it.
    """
    module_dir = testdir.copy_example("testmodulev2")
    with utils.module_v2_venv(
        module_dir, editable_install=testmodulev2_editable_install
    ) as venv:
        yield venv


@pytest.fixture(scope="function")
def testmodulev2_venv_active(
    deactive_venv: None,
    testmodulev2_venv: env.VirtualEnv,
) -> Iterator[env.VirtualEnv]:
    """
    Activates a Python environment with testmodulev2 installed in it for the currently running process.
    """
    with utils.activate_venv(testmodulev2_venv) as venv:
        yield venv


@pytest.mark.parametrize("testmodulev2_editable_install", [False, True])
def test_basic_example(
    testdir: pytest.Testdir,
    caplog: pytest.LogCaptureFixture,
    testmodulev2_venv_active: env.VirtualEnv,
    testmodulev2_editable_install: bool,
) -> None:
    """
    Make sure that our plugin works for v2 modules.
    """
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        result = testdir.runpytest_inprocess("tests/test_basics.py")
        result.assert_outcomes(passed=1)

        if not testmodulev2_editable_install:
            # The testmodulev2_venv_active fixture does not install the module in editable mode. For pytest-inmanta tests
            # this is fine but for module testing this is likely a mistake. Verify that the plugin raises an appropriate
            # warning.
            assert (
                "The module being tested is not installed in editable mode."
                " As a result the tests will not pick up any changes to the local source files."
                " To install it in editable mode, run `inmanta module install -e .`."
                in caplog.messages
            )


def test_basic_example_no_install(testdir: pytest.Testdir) -> None:
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


@pytest.mark.parametrize("testmodulev2_editable_install", [True])
def test_import(
    testdir: pytest.Testdir, testmodulev2_venv_active: env.VirtualEnv
) -> None:
    """
    Make sure that our plugin works for v2 modules.
    """
    result = testdir.runpytest_inprocess("tests/test_import.py")

    result.assert_outcomes(passed=3)
