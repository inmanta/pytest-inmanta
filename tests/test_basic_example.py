

def test_basic_example(testdir):
    """Make sure that our plugin works."""

    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_stuff.py")

    result.assert_outcomes(passed=1)