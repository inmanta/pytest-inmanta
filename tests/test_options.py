import os
import shutil

import pytest_inmanta

def test_module_in_place(testdir):
    """Make sure the run in place option works"""

    # Moving module to make sure we can run in place,
    # by making sure the module name in module.yml is in it's parent path
    testdir.copy_example("testmodule")
    os.mkdir("testmodule")
    shutil.move("model", "testmodule/model")
    shutil.move("module.yml", "testmodule/module.yml")
    shutil.move("plugins", "testmodule/plugins")
    shutil.move("tests", "testmodule/tests")
    os.chdir("testmodule")
    pytest_inmanta.plugin.CURDIR = (os.getcwd())

    result = testdir.runpytest("tests/test_resource_run.py", "--use-module-in-place")

    result.assert_outcomes(passed=1)
