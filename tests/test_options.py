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
import uuid


def test_removed_option_environment_variable_warning(testdir, monkeypatch):
    """
    A warning is shown when the environment variable of a removed option is set.
    """
    testdir.copy_example("testmodulev2")
    monkeypatch.setenv("INMANTA_MODULE_REPO", "package:https://example.com/simple")

    result = testdir.runpytest("--collect-only")

    assert (
        "The INMANTA_MODULE_REPO environment variable is set, but pytest-inmanta ignores it."
        " Use --pip-index-url or PIP_INDEX_URL to set the package indexes."
    ) in result.stdout.str()


def test_not_existing_venv_option(testdir, tmpdir):
    testdir.copy_example("testmodule")
    venv_path = os.path.join(tmpdir, str(uuid.uuid4()))

    result = testdir.runpytest("tests/test_resource_run.py", "--venv", venv_path)

    result.assert_outcomes(errors=1)
    assert f"Specified venv {venv_path} does not exist" in "\n".join(result.outlines)
