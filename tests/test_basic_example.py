"""
    Copyright 2019 Inmanta

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


def test_basic_example(testdir):
    """Make sure that our plugin works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_resource_run.py")

    result.assert_outcomes(passed=1)


def test_dryrun_example(testdir):
    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_dryrun.py")

    result.assert_outcomes(passed=1)


def test_run_sync(testdir):
    """Make sure that the run_sync mock works."""

    testdir.copy_example("testsync")

    result = testdir.runpytest("tests/test_stuff.py")

    result.assert_outcomes(passed=1)


def test_run_reflection(testdir):
    """Make sure that the run_sync mock works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_reflection.py")

    result.assert_outcomes(passed=1)


def test_run_capture(testdir):
    """Make sure that the run_sync mock works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_capture.py")

    result.assert_outcomes(passed=1)


def test_fixture_reset(testdir):
    """Make sure that the run_sync mock works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_reset.py")

    result.assert_outcomes(passed=2)


def test_badlog(testdir):
    """Make sure that the run_sync mock works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_BadLog.py")

    result.assert_outcomes(xfailed=1)


def test_resource_bad_id_attribute(testdir):
    """Make sure a deprecation warning is shown if an id_attribute called 'id' is found."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_resource_bad_id_attribute.py")

    result.assert_outcomes(passed=1)
    assert (
        "In one of the next major releases of inmanta-core it will not be possible anymore "
        "to use an id_attribute called id for testmodule::ResourceBadIdAttribute"
    ) in result.stdout.str()


def test_release_mode_validation(testdir):
    """Set invalid release mode"""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_resource_run.py", "--install_mode", "other")
    assert (
        "error: argument --install_mode: invalid choice: 'other' (choose from"
        in "\n".join(result.errlines)
    )


def test_multiple_repo_paths_option(testdir):
    testdir.copy_example("testmodule")

    result = testdir.runpytest(
        "tests/test_multiple_repo_paths.py",
        "--module_repo",
        "https://github.com/inmanta2/ https://github.com/inmanta/",
    )
    result.assert_outcomes(passed=1)


def test_multiple_repo_paths_multiple_options(testdir):
    testdir.copy_example("testmodule")

    result = testdir.runpytest(
        "tests/test_multiple_repo_paths.py",
        "--module_repo",
        "https://github.com/inmanta2/",
        "--module_repo",
        "https://github.com/inmanta/",
    )
    result.assert_outcomes(passed=1)


def test_multiple_repo_paths_env(testdir, monkeypatch):
    monkeypatch.setenv(
        "INMANTA_MODULE_REPO",
        "https://github.com/inmanta2/ https://github.com/inmanta/",
    )
    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_multiple_repo_paths.py")
    result.assert_outcomes(passed=1)


def test_import(testdir):
    """Make sure that importing functions works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_import.py")

    result.assert_outcomes(passed=5)


def test_project_no_plugins(testdir):
    """Make sure that using the project_no_plugins shows a warning."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_project_no_plugins.py")

    result.assert_outcomes(passed=1)
    assert (
        "DeprecationWarning: The project_no_plugins fixture is deprecated"
        " in favor of the INMANTA_NO_LOAD_PLUGINS environment variable."
    ) in result.stdout.str()


def test_state(testdir):
    """Make sure that importing functions works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_state.py")

    result.assert_outcomes(passed=2)


def test_cwd(testdir):
    """Ensure that the project fixture resets the cwd after each test case."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_cwd.py")

    result.assert_outcomes(passed=2)
