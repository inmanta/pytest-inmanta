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

import os
import tempfile

import pytest_inmanta.plugin
import utils
from inmanta import env


def test_transitive_v2_dependencies(examples_v2_package_index, pytestconfig, testdir):
    # set working directory to allow in-place with all example modules
    pytest_inmanta.plugin.CURDIR = str(
        pytestconfig.rootpath / "examples" / "test_dependencies_head"
    )

    testdir.copy_example("test_dependencies_head")

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
                + os.environ.get("PIP_INDEX_URL", "package:https://pypi.org/simple"),
            )
            result.assert_outcomes(passed=1)
        finally:
            utils.unload_modules_for_path(venv.site_packages_dir)


def test_conflicing_dependencies_strict(
    examples_v2_package_index, pytestconfig, testdir
):
    # set working directory to allow in-place with all example modules
    pytest_inmanta.plugin.CURDIR = str(
        pytestconfig.rootpath / "examples" / "test_conflict_dependencies"
    )
    """
    when using the pytest-inmanta without specifying the --no-strict-deps-check, the constraints
    of the installed modules/packages are veryfied and if a conflict is detected a ConflictingRequirement
    error is raised
    """
    testdir.copy_example("test_conflict_dependencies")

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
                + os.environ.get("PIP_INDEX_URL", "package:https://pypi.org/simple"),
            )
            result.assert_outcomes(errors=1)
            assert "ConflictingRequirements" "\n".join(result.outlines)
        finally:
            utils.unload_modules_for_path(venv.site_packages_dir)


def test_conflicing_dependencies_no_strict(
    examples_v2_package_index, pytestconfig, testdir
):
    """
    when using pytest-inmanta with --no-strict-deps-check option,
    the legacy check on the constraints is done. If the installed modules are not compatible
    a CompilerException is raised. In the used exemple for this test,
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
                "--no-strict-deps-check",
                "--use-module-in-place",
                # add pip index containing examples packages as module repo
                "--module_repo",
                f"package:{examples_v2_package_index}",
                # include configured pip index for inmanta-module-std
                "--module_repo",
                "package:"
                + os.environ.get("PIP_INDEX_URL", "package:https://pypi.org/simple"),
            )
            result.assert_outcomes(errors=1)
            assert "CompilerException" in "\n".join(result.outlines)
        finally:
            utils.unload_modules_for_path(venv.site_packages_dir)
