"""
    Copyright 2020 Inmanta

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
import os
import shutil
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
    pytest_inmanta.plugin.CURDIR = path

    result = testdir.runpytest("tests/test_location.py", "--use-module-in-place")

    result.assert_outcomes(passed=1)

    assert os.path.exists(os.path.join(path, "testfile"))


def test_not_existing_venv_option(testdir, tmpdir):
    testdir.copy_example("testmodule")
    venv_path = os.path.join(tmpdir, str(uuid.uuid4()))

    result = testdir.runpytest("tests/test_resource_run.py", "--venv", venv_path)

    result.assert_outcomes(errors=1)
    assert f"Specified venv {venv_path} does not exist" in "\n".join(result.outlines)
