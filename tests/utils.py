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

import contextlib
import importlib
import os
import subprocess
import sys
import tempfile
from importlib.abc import Loader
from types import ModuleType
from typing import Iterator, Optional, Sequence, Tuple

import inmanta.util
from inmanta import env
from inmanta.moduletool import ModuleTool
from packaging.version import Version


@contextlib.contextmanager
def module_v2_venv(
    module_path: str, *, editable_install: bool = False
) -> Iterator[env.VirtualEnv]:
    """
    Yields a Python environment with the given module installed in it.
    """
    with tempfile.TemporaryDirectory() as venv_dir:
        # set up environment
        venv: env.VirtualEnv = env.VirtualEnv(env_path=venv_dir)
        venv.init_env()
        venv_unset_python_path(venv)
        # install test module into environment

        if Version(inmanta.__version__) < Version("11.0"):
            # Pre iso 7
            # Base command to run the installation of a module
            install_command = [
                venv.python_path,
                "-m",
                "inmanta.app",
                "-X",
                "module",
                "install",
            ]

            if editable_install:
                # Editable install, add editable option
                install_command.append("-e")

            install_command.append(module_path)

            # Run the install command
            subprocess.check_call(install_command)
        else:
            # ISO 7, module install doesn't exist
            if editable_install:
                install_command = [
                    venv.python_path,
                    "-m",
                    "pip",
                    "install",
                    "-e",
                    module_path,
                ]
                subprocess.check_call(install_command)
            else:
                mod_artifact_path = ModuleTool().build(path=module_path)
                install_command = [
                    venv.python_path,
                    "-m",
                    "pip",
                    "install",
                    mod_artifact_path,
                ]
                subprocess.check_call(install_command)

        yield venv


@contextlib.contextmanager
def activate_venv(venv: env.VirtualEnv) -> Iterator[env.VirtualEnv]:
    """
    Activates a given Python environment for the currently running process. To prevent
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a unique venv dir to prevent caching issues with inmanta_plugins' submodule_search_locations
        unique_env_dir: str = os.path.join(tmpdir, ".env")
        os.symlink(venv.env_path, unique_env_dir)
        unique_env: env.VirtualEnv = env.VirtualEnv(env_path=unique_env_dir)
        unique_env.use_virtual_env()
        try:
            yield unique_env
        finally:
            unload_modules_for_path(unique_env.site_packages_dir)


def venv_unset_python_path(venv: env.VirtualEnv) -> None:
    """
    Workaround for pypa/build#405: unset PYTHONPATH because it's not required in this case and it triggers a bug in build
    """
    sitecustomize_existing: Optional[
        Tuple[Optional[str], Loader]
    ] = env.ActiveEnv.get_module_file("sitecustomize")
    # inherit from existing sitecustomize.py
    sitecustomize_inherit: str
    if sitecustomize_existing is not None and sitecustomize_existing[0] is not None:
        with open(sitecustomize_existing[0], "r") as fd:
            sitecustomize_inherit = fd.read()
    else:
        sitecustomize_inherit = ""
    with open(os.path.join(venv.site_packages_dir, "sitecustomize.py"), "a") as fd:
        fd.write(
            f"""
{sitecustomize_inherit}

import os

if "PYTHONPATH" in os.environ:
    del os.environ["PYTHONPATH"]
            """.strip()
        )


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
