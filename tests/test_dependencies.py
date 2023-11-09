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
import logging
import os
import tempfile

import pytest

import pytest_inmanta.plugin
import utils
from inmanta import env
from pytest_inmanta.core import (
    SUPPORTS_LEGACY_PROJECT_PIP_INDEX,
    SUPPORTS_PROJECT_PIP_INDEX,
)
from pytest_inmanta.parameters import pip_index_url


def test_transitive_v2_dependencies(
    examples_v2_package_index, pytestconfig, testdir, caplog
):
    # set working directory to allow in-place with all example modules
    pytest_inmanta.plugin.CURDIR = str(
        pytestconfig.rootpath / "examples" / "test_dependencies_head"
    )

    testdir.copy_example("test_dependencies_head")

    with caplog.at_level(logging.WARNING):
        with tempfile.TemporaryDirectory() as venv_dir:
            # set up environment
            venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
            try:
                venv.use_virtual_env()

                # run tests
                result = testdir.runpytest_inprocess(
                    "tests/test_basics.py",
                    "--use-module-in-place",
                    # add pip index containing examples packages as module repo
                    "--pip-index-url",
                    f"{examples_v2_package_index}",
                    # include configured pip index for inmanta-module-std
                    "--pip-index-url",
                    f'{os.environ.get("PIP_INDEX_URL", "https://pypi.org/simple")}',
                )
                result.assert_outcomes(passed=1)
            finally:
                utils.unload_modules_for_path(venv.site_packages_dir)

        if not SUPPORTS_LEGACY_PROJECT_PIP_INDEX:
            warning_msg: str = (
                "Setting a project-wide pip index is not supported on this version of inmanta-core. "
                "The provided index will be used as a v2 package source"
            )
            assert warning_msg in caplog.text


@pytest.mark.parametrize(
    "no_strict_deps_check, error_msg",
    [
        (True, "CompilerException"),
        (False, "ConflictingRequirements"),
    ],
)
def test_conflicing_dependencies(
    examples_v2_package_index, pytestconfig, testdir, no_strict_deps_check, error_msg
):
    """
    when using the pytest-inmanta without specifying the --no-strict-deps-check, the constraints
    of the installed modules/packages are verified and if a conflict is detected a ConflictingRequirement
    error is raised.
    when using pytest-inmanta with --no-strict-deps-check option,
    the legacy check on the constraints is done. If the installed modules are not compatible
    a CompilerException is raised. In the used example for this test,
    test_conflict_dependencies(v1 module) requires inmanta-module-testmodulev2conflict1 and
    inmanta-module-testmodulev2conflict2. The later two are incompatible as one requires lorem 0.0.1
    and the other one 0.1.1.
    """
    # set working directory to allow in-place with all example modules
    pytest_inmanta.plugin.CURDIR = str(
        pytestconfig.rootpath / "examples" / "test_conflict_dependencies"
    )
    testdir.copy_example("test_conflict_dependencies")

    with tempfile.TemporaryDirectory() as venv_dir:
        # set up environment
        venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
        try:
            venv.use_virtual_env()

            # run tests
            result = testdir.runpytest_inprocess(
                "tests/test_basics.py",
                *(["--no-strict-deps-check"] if no_strict_deps_check else []),
                "--use-module-in-place",
                # add pip index containing examples packages as module repo
                "--pip-index-url",
                f"{examples_v2_package_index}",
                # include configured pip index for inmanta-module-std and lorem
                "--pip-index-url",
                f'{os.environ.get("PIP_INDEX_URL", "https://pypi.org/simple")}',
            )
            result.assert_outcomes(errors=1)
            assert error_msg in "\n".join(result.outlines)
        finally:
            utils.unload_modules_for_path(venv.site_packages_dir)


def test_transitive_v2_dependencies_legacy_warning(
    examples_v2_package_index, pytestconfig, testdir, caplog
):
    # set working directory to allow in-place with all example modules
    pytest_inmanta.plugin.CURDIR = str(
        pytestconfig.rootpath / "examples" / "test_dependencies_head"
    )

    testdir.copy_example("test_dependencies_head")

    with caplog.at_level(logging.WARNING):
        with tempfile.TemporaryDirectory() as venv_dir:
            # set up environment
            venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
            try:
                venv.use_virtual_env()

                # run tests
                result = testdir.runpytest_inprocess(
                    "tests/test_basics.py",
                    "--use-module-in-place",
                    # add pip index containing examples packages as module repo
                    "--module_repo",
                    f"package:{examples_v2_package_index}",
                    # include configured pip index for inmanta-module-std
                    "--module_repo",
                    "package:"
                    + os.environ.get("PIP_INDEX_URL", "https://pypi.org/simple"),
                )
                result.assert_outcomes(passed=1)
            finally:
                utils.unload_modules_for_path(venv.site_packages_dir)

        if SUPPORTS_LEGACY_PROJECT_PIP_INDEX:
            warning_msg: str = (
                "Setting a package source through the --module-repo <index_url> cli option with type `package` "
                "is now deprecated and will raise a warning during compilation."
                " Use the --pip-index-url <index_url> pytest option instead or set"
                f" the {pip_index_url.environment_variable} environment variable to address these warnings. "
            )
            assert warning_msg in caplog.text


def test_transitive_v2_dependencies_legacy_warning_for_env_var(
    examples_v2_package_index, pytestconfig, testdir, caplog, monkeypatch
):
    # set working directory to allow in-place with all example modules
    pytest_inmanta.plugin.CURDIR = str(
        pytestconfig.rootpath / "examples" / "test_dependencies_head"
    )

    testdir.copy_example("test_dependencies_head")

    with caplog.at_level(logging.WARNING):
        with tempfile.TemporaryDirectory() as venv_dir:
            # set up environment
            venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
            try:
                venv.use_virtual_env()
                env_index = os.environ.get("PIP_INDEX_URL", "https://pypi.org/simple")

                monkeypatch.delenv("PIP_INDEX_URL", raising=False)
                monkeypatch.setenv(
                    "INMANTA_PIP_INDEX_URL", f"{examples_v2_package_index} {env_index}"
                )
                # run tests
                result = testdir.runpytest_inprocess(
                    "tests/test_basics.py",
                    "--use-module-in-place",
                )
                result.assert_outcomes(passed=1)
            finally:
                utils.unload_modules_for_path(venv.site_packages_dir)

        if SUPPORTS_PROJECT_PIP_INDEX:
            warning_msg: str = "usage of INMANTA_PIP_INDEX_URL is deprecated, use PIP_INDEX_URL instead"
            assert warning_msg in caplog.text


def test_transitive_v2_dependencies_no_index_warning(
    examples_v2_package_index, pytestconfig, testdir, caplog, monkeypatch
):
    # set working directory to allow in-place with all example modules
    pytest_inmanta.plugin.CURDIR = str(
        pytestconfig.rootpath / "examples" / "test_dependencies_head"
    )

    testdir.copy_example("test_dependencies_head")

    with caplog.at_level(logging.WARNING):
        with tempfile.TemporaryDirectory() as venv_dir:
            # set up environment
            venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
            try:
                venv.use_virtual_env()
                monkeypatch.delenv("PIP_INDEX_URL", raising=False)
                # run tests
                result = testdir.runpytest_inprocess(
                    "tests/test_basics.py",
                    "--use-module-in-place",
                )
                result.assert_outcomes(errors=1)  # fail, as no pip index is set
            finally:
                utils.unload_modules_for_path(venv.site_packages_dir)

        if SUPPORTS_PROJECT_PIP_INDEX:
            warning_msg: str = "No pip config source is configured, any attempt to perform a pip install will fail."
            assert warning_msg in caplog.text
