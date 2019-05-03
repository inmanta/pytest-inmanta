

def test_basic_example(testdir):
    """Make sure that our plugin works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_stuff.py")

    result.assert_outcomes(passed=1)


def test_run_sync(testdir):
    """Make sure that the run_sync mock works."""

    testdir.copy_example("testsync")

    result = testdir.runpytest("tests/test_stuff.py")

    result.assert_outcomes(passed=1)


def test_badlog(testdir):
    """Make sure that the run_sync mock works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_BadLog.py")

    result.assert_outcomes(failed=1)