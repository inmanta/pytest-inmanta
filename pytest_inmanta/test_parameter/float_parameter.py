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
from .parameter import TestParameter


class FloatTestParameter(TestParameter[float]):
    """
    A test parameter that should contain an float value.  The option will store the value
    as a string and convert it to a float.

    .. code-block:: python

        inm_test_timeout = FloatTestParameter(
            argument="--test-timeout",
            environment_variable="INMANTA_TEST_TIMEOUT",
            usage="Delay before which the test should timeout",
            default=15.64,
            group=param_group,
        )

    """

    def validate(self, raw_value: object) -> float:
        return float(str(raw_value))
