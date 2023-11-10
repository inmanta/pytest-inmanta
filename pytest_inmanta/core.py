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

from typing import Optional

import pkg_resources
from pkg_resources import DistributionNotFound

from packaging import version

CORE_VERSION: Optional[version.Version]
"""
Version of the inmanta-core package. None if it is not installed.
"""

try:
    CORE_VERSION = version.Version(
        pkg_resources.get_distribution("inmanta-core").version
    )
except DistributionNotFound:
    CORE_VERSION = None

# Setting a project-wide pip index is only supported for iso7+
SUPPORTS_PROJECT_PIP_INDEX: bool = (
    CORE_VERSION is not None and CORE_VERSION >= version.Version("11.0.0.dev")
)


SUPPORTS_LEGACY_PROJECT_PIP_INDEX: bool = (
    CORE_VERSION is not None and CORE_VERSION >= version.Version("9.0.0.dev")
)

SUPPORTS_MODULES_V2: bool = (
    CORE_VERSION is not None and CORE_VERSION >= version.Version("6.dev")
)
