import os
import shutil
import tempfile
import uuid

import pytest_inmanta

def test_module_in_place(testdir):
    """Make sure the run in place option works"""

    # copy_example copies what is IN the given directory, not the directory itself...
    testdir.copy_example("testmodule")
    # Moving module to make sure we can run in place,
    # by making sure the module name in module.yml is in it's parent path
    os.mkdir("testmodule")
    shutil.move("model", "testmodule/model")
    shutil.move("module.yml", "testmodule/module.yml")
    shutil.move("plugins", "testmodule/plugins")
    shutil.move("tests", "testmodule/tests")

    os.chdir("testmodule")
    path = os.getcwd()
    assert not os.path.exists(os.path.join(path, "testfile"))
    pytest_inmanta.plugin.CURDIR = (path)

    result = testdir.runpytest("tests/test_location.py", "--use-module-in-place")

    result.assert_outcomes(passed=1)

    assert os.path.exists(os.path.join(path, "testfile"))


def test_not_existing_venv_option(testdir):
    testdir.copy_example("testmodule")

    result = testdir.runpytest("tests/test_resource_run.py", "--venv", os.path.join(tempfile.gettempdir(), str(uuid.uuid4())))

    result.assert_outcomes(error=1)
