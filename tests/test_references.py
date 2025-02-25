"""
Copyright 2025 Inmanta

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

import pytest

import utils
from pytest_inmanta.core import SUPPORTS_REFERENCE

if not SUPPORTS_REFERENCE:
    pytest.skip(
        "Skipping reference tests.",
        allow_module_level=True,
    )


def test_basic_refs(testdir: pytest.Testdir, deactive_venv) -> None:
    """
    Run the references tests.
    """
    module_dir = testdir.copy_example("refs")
    with utils.module_v2_venv(module_dir, editable_install=True) as venv:
        with utils.activate_venv(venv):
            result = testdir.runpytest_inprocess("tests/test_refs.py")

    result.assert_outcomes(passed=1)
