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

import pathlib
import subprocess
import sys

import pytest

import pytest_inmanta.plugin
from inmanta import module

# be careful not to import any core>=6 objects directly
from pytest_inmanta.core import SUPPORTS_MODULES_V2

if not SUPPORTS_MODULES_V2:
    pytest.skip(
        "Skipping modules v2 tests for inmanta-core<6 (pre modules v2).",
        allow_module_level=True,
    )


def test_v2_module_under_test_on_core_without_v1(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """
    On a core without V1 support, a V2 module under test goes through the V2 install check.
    """
    module_dir = pathlib.Path(__file__).parent.parent / "examples" / "testmodulev2"
    module_under_test = module.ModuleV2(None, str(module_dir))
    monkeypatch.setattr(
        pytest_inmanta.plugin,
        "get_module",
        lambda: (module_under_test, str(module_dir)),
    )
    monkeypatch.delattr(module, "ModuleV1")

    # The example module isn't installed in this venv
    with pytest.raises(Exception, match="The module being tested is not installed"):
        pytest_inmanta.plugin.ensure_current_module_install(str(tmp_path))
    assert list(tmp_path.iterdir()) == []


def test_plugin_loads_on_core_without_v1_project_settings() -> None:
    """
    The plugin loads on a core without InstallMode, ModuleRepoType and ModuleRepoInfo.
    """
    code = (
        "import inmanta.module as m;"
        " del m.InstallMode, m.ModuleRepoType, m.ModuleRepoInfo;"
        " import pytest_inmanta.plugin"
    )
    subprocess.run([sys.executable, "-c", code], check=True)
