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
from enum import Enum
from typing import Container, Optional, Type, TypeVar

from .parameter import TestParameter

E = TypeVar("E", bound=Enum)


class EnumTestParameter(TestParameter[E]):
    """
    A test parameter that should contain an enumeration value.  The option will store a string value
    but it will only accepts values from the provided enum.

    .. code-block:: python

        inm_install_mode = EnumTestParameter(
            argument="--install_mode",
            environment_variable="INMANTA_INSTALL_MODE",
            usage="Install mode for modules downloaded during this test",
            enum=InstallMode,
            default=InstallMode.release,
            group=param_group,
        )

    """

    def __init__(
        self,
        argument: str,
        environment_variable: str,
        usage: str,
        *,
        enum: Type[E],
        default: Optional[E] = None,
        key: Optional[str] = None,
        group: Optional[str] = None,
        legacy: Optional["EnumTestParameter[E]"] = None,
    ) -> None:
        self.enum = enum
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
    def choices(self) -> Optional[Container[str]]:
        return [str(item.value) for item in self.enum]

    def validate(self, raw_value: object) -> E:
        return self.enum(raw_value)
