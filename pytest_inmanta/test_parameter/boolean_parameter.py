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
from typing import Optional

from .parameter import TestParameter


class BooleanTestParameter(TestParameter[bool]):
    """
    A test parameter that should contain a boolean value.  The option will act as a flag.
    If it is not set, the default value will be used when resolved.  If it is set, the opposite
    of the default value is resolved.  If the option is set via environment variable, the value
    should, once "stripped" of any space, and transformed to lower case, evaluate to either "true"
    or "false".  The resolved value would then be, respectively, True or False.

    .. code-block:: python

        inm_mod_in_place = BooleanTestParameter(
            argument="--use-module-in-place",
            environment_variable="INMANTA_USE_MODULE_IN_PLACE",
            usage=(
                "tell pytest-inmanta to run with the module in place, useful for debugging. "
                "Makes inmanta add the parent directory of your module directory to it's directory path, "
                "instead of copying your module to a temporary libs directory. "
                "It allows testing the current module against specific versions of dependent modules. "
                "Using this option can speed up the tests, because the module dependencies are not downloaded multiple times."
            ),
            group=param_group,
        )

    """

    def __init__(
        self,
        argument: str,
        environment_variable: str,
        usage: str,
        *,
        default=False,
        key: Optional[str] = None,
        group: Optional[str] = None,
        legacy: Optional["BooleanTestParameter"] = None,
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
        if self.default is True:
            return "store_false"

        return "store_true"

    def validate(self, raw_value: object) -> bool:
        parsed = str(raw_value).lower().strip()
        if parsed == "false":
            return False

        if parsed == "true":
            return True

        raise ValueError(
            f"Boolean env var should be set to either 'true' or 'false', got '{parsed}' instead"
        )
