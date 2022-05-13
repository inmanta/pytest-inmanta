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
import collections
import os
from typing import Optional, Sequence

try:
    """
    Those classes are only used in type annotation, but the import doesn't work
    in python 3.6.  So we simply catch the error and ignore it.
    """
    from pytest import Config
except ImportError:
    pass

from .parameter import ParameterNotSetException, TestParameter


class ListTestParameter(TestParameter[Sequence[str]]):
    """
    A test parameter that should contain a list of string.  For each mention of the option, the value
    will be added to the string.  If the value is passed as an environment variable, the string will
    be splitted in each space.

    .. code-block:: python

        inm_mod_repo = ListTestParameter(
            argument="--module_repo",
            environment_variable="INMANTA_MODULE_REPO",
            usage=(
                "Location to download modules from."
                "Can be specified multiple times to add multiple locations"
            ),
            default=["https://github.com/inmanta/"],
            group=param_group,
        )

    """

    def __init__(
        self,
        argument: str,
        environment_variable: str,
        usage: str,
        *,
        default: Optional[Sequence[str]] = None,
        key: Optional[str] = None,
        group: Optional[str] = None,
        legacy: Optional["ListTestParameter"] = None,
    ) -> None:
        super().__init__(
            argument,
            environment_variable,
            usage,
            default=default,
            key=key,
            group=group,
            legacy=legacy,
        )

    @property
    def action(self) -> str:
        return "append"

    def validate(self, raw_value: object) -> Sequence[str]:
        if not isinstance(raw_value, collections.abc.Sequence):
            raise ValueError(
                f"Type of {raw_value} is {type(raw_value)}, expected sequence"
            )

        return [str(item) for item in raw_value]

    def resolve(self, config: "Config") -> Sequence[str]:
        option = config.getoption(self.argument, default=self.default)
        if option is not None and option is not self.default:
            # A value is set, and it is not the default one
            if isinstance(option, collections.abc.Sequence):
                return self.validate(option)
            else:
                return self.validate([option])

        env_var = os.getenv(self.environment_variable)
        if env_var is not None:
            # A value is set
            return self.validate(env_var.split(" "))

        if self.default is not None:
            return self.default

        raise ParameterNotSetException(self)
