"""
    Copyright 2023 Inmanta

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
from typing import Optional, Type, Union

from pytest_inmanta.test_parameter.boolean_parameter import BooleanTestParameter
from pytest_inmanta.test_parameter.parameter import DynamicDefault


class OptionalBooleanTestParameter(BooleanTestParameter):
    """
    A test parameter that should contain a boolean value that can be set, unset or None

    It produces a positive and negative options e.g. `--pip-pre` and `--no-pip-pre`

    In case of None, the default value is used
    """

    def __init__(
        self,
        argument: str,
        environment_variable: str,
        usage: str,
        *,
        default: Optional[Union[bool, DynamicDefault[bool]]] = None,
        key: Optional[str] = None,
        group: Optional[str] = None,
        legacy_environment_variable: Optional[str] = None,
    ) -> None:
        super().__init__(
            argument,
            environment_variable,
            usage,
            key=key,
            group=group,
            default=default,
            legacy_environment_variable=legacy_environment_variable,
        )

    @property
    def action(self) -> Type[argparse.Action]:
        return argparse.BooleanOptionalAction
