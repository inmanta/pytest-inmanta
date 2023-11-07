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
from typing import Callable, Optional, Type, Union

from pytest_inmanta.test_parameter.boolean_parameter import BooleanTestParameter
from pytest_inmanta.test_parameter.parameter import (
    DynamicDefault,
    ParameterNotSetException,
)

try:
    """
    Those classes are only used in type annotation, but the import doesn't work
    in python 3.6.  So we simply catch the error and ignore it.
    """
    from pytest import Parser
except ImportError:
    pass


class OptionalBooleanTestParameter(BooleanTestParameter):
    """
    A test parameter that should contain a boolean value that can be set, unset or None

    In case of None, the fallback function is called
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
    ) -> None:
        super().__init__(
            argument,
            environment_variable,
            usage,
            key=key,
            group=group,
            default=default,
        )

    @property
    def action(self) -> Type[argparse.Action]:
        return argparse.BooleanOptionalAction
