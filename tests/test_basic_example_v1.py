"""
Copyright 2026 Inmanta

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

from inmanta import module

if not hasattr(module, "ModuleV1"):
    pytest.skip(
        "Skipping V1 module tests for inmanta-core versions without V1 modules.",
        allow_module_level=True,
    )


def test_module_under_test_v1(testdir: pytest.Testdir) -> None:
    """
    Make sure that the plugin compiles a V1 module under test, with its plugins.
    """
    testdir.copy_example("testmodulev1")

    result = testdir.runpytest("tests/test_compile.py")

    result.assert_outcomes(passed=1)
