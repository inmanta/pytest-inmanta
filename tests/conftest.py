"""
    Copyright 2018 Inmanta

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
import sys
from typing import Optional

import pkg_resources
import pytest

import pytest_inmanta.plugin
from inmanta import env
from inmanta.loader import PluginModuleFinder

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def set_cwd(testdir):
    pytest_inmanta.plugin.CURDIR = os.getcwd()


@pytest.fixture(scope="function", autouse=True)
def deactive_venv():
    old_os_path = os.environ.get("PATH", "")
    old_prefix = sys.prefix
    old_path = sys.path
    old_pythonpath = os.environ.get("PYTHONPATH", None)
    old_os_venv: Optional[str] = os.environ.get("VIRTUAL_ENV", None)
    old_working_set = pkg_resources.working_set

    yield

    os.environ["PATH"] = old_os_path
    sys.prefix = old_prefix
    sys.path = old_path
    pkg_resources.working_set = old_working_set
    # Restore PYTHONPATH
    if old_pythonpath is not None:
        os.environ["PYTHONPATH"] = old_pythonpath
    elif "PYTHONPATH" in os.environ:
        del os.environ["PYTHONPATH"]
    # Restore VIRTUAL_ENV
    if old_os_venv is not None:
        os.environ["VIRTUAL_ENV"] = old_os_venv
    elif "VIRTUAL_ENV" in os.environ:
        del os.environ["VIRTUAL_ENV"]
    # stay compatible with older versions of core: don't call the function if it doesn't exist
    if hasattr(env, "mock_process_env"):
        env.mock_process_env(python_path=sys.executable)
    if hasattr(PluginModuleFinder, "reset"):
        PluginModuleFinder.reset()
