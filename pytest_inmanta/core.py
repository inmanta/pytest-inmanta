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

import importlib.metadata
from typing import Optional

import inmanta.export
from packaging import version

CORE_VERSION: Optional[version.Version]
"""
Version of the inmanta-core package. None if it is not installed.
"""

try:
    CORE_VERSION = version.Version(importlib.metadata.version("inmanta-core"))
except importlib.metadata.PackageNotFoundError:
    CORE_VERSION = None


SUPPORTS_MODULES_V2: bool = (
    CORE_VERSION is not None and CORE_VERSION >= version.Version("6.dev")
)

try:
    import inmanta.references  # noqa: F401

    SUPPORTS_REFERENCE = True
except ImportError:
    SUPPORTS_REFERENCE = False

CORE_DEPENDENCY_CYCLE_EXCEPTION: Optional[type[Exception]] = getattr(
    inmanta.export, "DependencyCycleException", None
)
"""
The exception raised by the exporter of inmanta-core when the requires relationships of the resources
contain a cycle. None when the exporter of the installed inmanta-core version doesn't detect cycles.
"""
