"""
    Copyright 2022 Inmanta

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
from inmanta.module import InstallMode
from test_parameter import PathTestParameter, BooleanTestParameter, ListTestParameter, EnumTestParameter

param_group = "pytest-inmanta"

inm_venv = PathTestParameter(
    argument="--venv",
    environment_variable="INMANTA_TEST_ENV",
    usage=(
        "folder in which to place the virtual env for tests (will be shared by all tests). "
        "This options depends on symlink support. This does not work on all windows versions. "
        "On windows 10 you need to run pytest in an admin shell. "
        "Using a fixed virtual environment can speed up running the tests."
    ),
    group=param_group,
)

inm_mod_in_place = BooleanTestParameter(
    argument="--use-module-in-place",
    environment_variable="INMANTA_USE_MODULE_IN_PLACE",
    usage=(
        "tell pytest-inmanta to run with the module in place, useful for debugging. "
        "Makes inmanta add the parent directory of your module directory to it's directory path, instead of copying your "
        "module to a temporary libs directory. "
        "It allows testing the current module against specific versions of dependent modules. "
        "Using this option can speed up the tests, because the module dependencies are not downloaded multiple times."
    ),
    group=param_group,
)

inm_mod_repo = ListTestParameter(
    argument="--module_repo",
    environment_variable="INMANTA_MODULE_REPO",
    usage=(
        "location to download modules from."
        "Can be specified multiple times to add multiple locations"
    ),
    default=["https://github.com/inmanta/"],
    group=param_group,
)

inm_install_mode = EnumTestParameter(
    argument="--install_mode",
    environment_variable="INMANTA_MODULE_REPO",
    usage="Install mode for modules downloaded during this test",
    enum=InstallMode,
    default=InstallMode.release,
    group=param_group,
)

# This option behaves slightly differently than --no_load_plugins
# If the environment variable is set, we check here that the value is the string "True"
# The former option accepts any non-empty string
# This is why the env var and the option names have been changed
inm_no_load_plugins = BooleanTestParameter(
    argument="--no-load-plugins",
    environment_variable="INMANTA_TEST_NO_LOAD_PLUGINS",
    usage=(
        "When not using this option during the testing of plugins with the `project.get_plugin_function` method, "
        "it's possible that the module's `plugin/__init__.py` is loaded multiple times, "
        "which can cause issues when it has side effects, as they are executed multiple times as well."
    )
)
