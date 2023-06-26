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


SUPPORTS_PROJECT_PIP_INDEX: bool = (
    CORE_VERSION is not None and CORE_VERSION >= version.Version("9.2.0.dev")
)
