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


class IntegerTestParameter(TestParameter[int]):
    """
    A test parameter that should contain an integer value.  The option will store the value
    as a string and convert it to an integer.

    .. code-block:: python

        inm_lsm_srv_port = IntegerTestParameter(
            argument="--lsm-srv-port",
            environment_variable="INMANTA_LSM_SRV_PORT",
            usage="Port the orchestrator api is listening to",
            default=8888,
            group=param_group,
        )

    """

    def validate(self, raw_value: object) -> int:
        return int(str(raw_value))
