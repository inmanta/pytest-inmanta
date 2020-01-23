import os
import shutil

import pytest_inmanta

def test_module_in_place(testdir):
    """Make sure the run in place option works"""

    # Moving module to make sure we can run in place,
    # by making sure the module name in module.yml is in it's parent path
    testdir.copy_example("testmodule_2")
    os.mkdir("testmodule")
    shutil.move("model", "testmodule/model")
    shutil.move("module.yml", "testmodule/module.yml")
    shutil.move("plugins", "testmodule/plugins")
    shutil.move("tests", "testmodule/tests")
    os.chdir("testmodule")
    path = os.getcwd()
    assert not os.path.exists(os.path.join(path, "testfile"))
    pytest_inmanta.plugin.CURDIR = (path)

    result = testdir.runpytest("tests/test_resource_run_2.py", "--use-module-in-place")

    result.assert_outcomes(passed=1)

    assert os.path.exists(os.path.join(path, "testfile"))
