"""
    Copyright 2021 Inmanta

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

import importlib
import sys
from typing import Optional, Sequence
from types import ModuleType


def unload_modules_for_path(path: str) -> None:
    """
    Unload any modules that are loaded from a given path.
    """

    def module_in_prefix(module: ModuleType, prefix: str) -> bool:
        file: Optional[str] = getattr(module, "__file__", None)
        return file.startswith(prefix) if file is not None else False

    loaded_modules: Sequence[str] = [
        mod_name for mod_name, mod in sys.modules.items() if module_in_prefix(mod, path)
    ]
    for mod_name in loaded_modules:
        del sys.modules[mod_name]
    importlib.invalidate_caches()
