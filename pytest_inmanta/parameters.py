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
import os

from inmanta.module import InstallMode

from .test_parameter import (
    BooleanTestParameter,
    EnumTestParameter,
    ListTestParameter,
    PathTestParameter,
)

try:
    """
    Those classes are only used in type annotation, but the import doesn't work
    in python 3.6.  So we simply catch the error and ignore it.
    """
    from pytest import Config
except ImportError:
    pass

param_group = "pytest-inmanta"

inm_venv = PathTestParameter(
    argument="--venv",
    environment_variable="INMANTA_TEST_ENV",
    usage=(
        "Folder in which to place the virtual env for tests (will be shared by all tests). "
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
        "Tell pytest-inmanta to run with the module in place, useful for debugging. "
        "Makes inmanta add the parent directory of your module directory to it's directory path, instead of copying your "
        "module to a temporary libs directory. "
        "It allows testing the current module against specific versions of dependent modules. "
        "Using this option can speed up the tests, because the module dependencies are not downloaded multiple times."
    ),
    group=param_group,
)

inm_no_strict_deps_check = BooleanTestParameter(
    argument="--no-strict-deps-check",
    environment_variable="INMANTA_NO_STRICT_DEPS_CHECKS",
    usage=(
        "Tell pytest-inmanta to run without using the deps check after module installation."
        " When using the dependency check, an error is raised if there are conflicting requirements"
        " when disabling the check, the less strict legacy behavior is used instead."
    ),
    default=False,
    group=param_group,
)


# This is the legacy module repo option
# TODO remove this in next major version bump
inm_mod_repo_legacy = ListTestParameter(
    argument="--module_repo",
    environment_variable="INMANTA_MODULE_REPO",
    usage=(
        "Location to download modules from."
        "Can be specified multiple times to add multiple locations"
    ),
)

inm_mod_repo = ListTestParameter(
    argument="--module-repo",
    environment_variable=inm_mod_repo_legacy.environment_variable,
    usage=inm_mod_repo_legacy.usage,
    default=["https://github.com/inmanta/"],
    group=param_group,
    legacy=inm_mod_repo_legacy,
)


# This is the legacy install mode option
# TODO remove this in next major version bump
inm_install_mode_legacy = EnumTestParameter(
    argument="--install_mode",
    environment_variable="INMANTA_INSTALL_MODE",
    usage="Install mode for modules downloaded during this test",
    enum=InstallMode,
)

inm_install_mode = EnumTestParameter(
    argument="--install-mode",
    environment_variable=inm_install_mode_legacy.environment_variable,
    usage=inm_install_mode_legacy.usage,
    enum=inm_install_mode_legacy.enum,
    default=InstallMode.release,
    group=param_group,
    legacy=inm_install_mode_legacy,
)


# This is the legacy no load plugins option
# TODO remove this in next major version bump
class _LegacyBooleanTestParameter(BooleanTestParameter):
    def resolve(self, config: "Config") -> bool:
        """
        The legacy option for --no-load-plugins requires some more treatment than the other
        as the behavior when the env variable is set is different.  Any non-empty string set
        in env variable means that the option is set, and we should not load the plugins.

        This helper function comes to overwrite the resolve method in the legacy option.
        """
        option = config.getoption(self.argument, default=None)
        if option is not None:
            # A value is set, and it is not the default one
            return self.validate(option)

        if os.getenv(self.environment_variable):
            return True

        return False


# This is the legacy no load plugins option
# TODO remove this in next major version bump
inm_no_load_plugins_legacy = _LegacyBooleanTestParameter(
    argument="--no_load_plugins",
    environment_variable="INMANTA_TEST_NO_LOAD_PLUGINS",
    usage=(
        "Don't load plugins in the Project class. Overrides INMANTA_TEST_NO_LOAD_PLUGINS."
        "The value of INMANTA_TEST_NO_LOAD_PLUGINS environment variable has to be a non-empty string to not load plugins."
        "When not using this option during the testing of plugins with the `project.get_plugin_function` method, "
        "it's possible that the module's `plugin/__init__.py` is loaded multiple times, "
        "which can cause issues when it has side effects, as they are executed multiple times as well."
    ),
)

# This option behaves slightly differently than --no_load_plugins
# If the environment variable is set, we check here that the value is the string "True"
# The former option accepts any non-empty string
# This is why the env var and the option names have been changed
inm_no_load_plugins = BooleanTestParameter(
    argument="--no-load-plugins",
    environment_variable="INMANTA_NO_LOAD_PLUGINS",
    usage=(
        "Don't load plugins in the Project class.  "
        "When not using this option during the testing of plugins with the `project.get_plugin_function` method, "
        "it's possible that the module's `plugin/__init__.py` is loaded multiple times, "
        "which can cause issues when it has side effects, as they are executed multiple times as well."
    ),
    legacy=inm_no_load_plugins_legacy,
)
