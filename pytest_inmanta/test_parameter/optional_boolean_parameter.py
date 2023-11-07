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
import argparse
import os
from typing import Callable, Optional, Type

from pytest_inmanta.test_parameter.boolean_parameter import BooleanTestParameter
from pytest_inmanta.test_parameter.parameter import ParameterNotSetException

try:
    """
    Those classes are only used in type annotation, but the import doesn't work
    in python 3.6.  So we simply catch the error and ignore it.
    """
    from pytest import Config, OptionGroup, Parser
except ImportError:
    pass


class OptionalBooleanTestParameter(BooleanTestParameter):
    """
    A test parameter that should contain a boolean value that can be set, unset or None

    In case of None, the fallback function is called

    .. code-block:: python

        inm_mod_in_place = BooleanTestParameter(
            argument="--pip-pre",
            environment_variable="INMANTA_PIP_PRE",
            usage=(
                "tell pytest-inmanta to run with the module in place, useful for debugging. "
                "Makes inmanta add the parent directory of your module directory to it's directory path, "
                "instead of copying your module to a temporary libs directory. "
                "It allows testing the current module against specific versions of dependent modules. "
                "Using this option can speed up the tests, because the module dependencies are not downloaded multiple times."
            ),
            group=param_group,
            fallback=
        )

    """

    def __init__(
        self,
        argument: str,
        environment_variable: str,
        usage: str,
        *,
        fallback: Optional[Callable[["Config"], bool]] = None,
        key: Optional[str] = None,
        group: Optional[str] = None,
    ) -> None:
        super().__init__(
            argument,
            environment_variable,
            usage,
            key=key,
            group=group,
        )
        self.fallback = fallback

    @property
    def action(self) -> Type[argparse.Action]:
        return argparse.BooleanOptionalAction

    def resolve(self, config: "Config") -> bool:
        """
        Resolve the test parameter.
        First, we try to get it from the provided options.
        Second, we try to get it from environment variables.
        Then, if there is a default, we use it.
        Finally, if none of the above worked, we raise a ParameterNotSetException.
        """
        option = config.getoption(self.argument, default=None)
        if option is not None:
            # A value is set, and it is not the default one
            return self.validate(option)

        env_var = os.getenv(self.environment_variable)
        if env_var is not None:
            # A value is set
            return self.validate(env_var)

        if self.fallback:
            return self.fallback(config)

        raise ParameterNotSetException(self)
