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
from enum import Enum
from typing import Container, Optional, Sequence, Union

from _pytest.config import Config

from .parameter import ParameterNotSetException, TestParameter


class ListTestParameter(TestParameter[Sequence[str]]):
    """
    A test parameter that should contain a boolean value
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
    ) -> None:
        super().__init__(
            argument, environment_variable, usage, default=default, key=key, group=group
        )

    @property
    def action(self) -> str:
        return "append"

    def validate(self, raw_value: object) -> Sequence[str]:
        if not isinstance(raw_value, collections.Sequence):
            raise ValueError(
                f"Type of {raw_value} is {type(raw_value)}, expected sequence"
            )

        return [str(item) for item in raw_value]

    def resolve(self, config: Config) -> Sequence[str]:
        option = config.getoption(self.argument, default=self.default)
        if option is not None and option is not self.default:
            # A value is set, and it is not the default one
            if isinstance(option, list):
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
