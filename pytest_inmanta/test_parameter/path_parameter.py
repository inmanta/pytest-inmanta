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

import os
from pathlib import Path
from typing import Optional, Union

import pytest_inmanta.plugin
from pytest_inmanta.test_parameter.parameter import DynamicDefault, TestParameter


def abspath(path: str, *, source: str) -> str:
    """
    Compute absolute path from relative or absolute path

    :param path: path of the object
    :param source: base directory to use when the path is relative
    """
    return path if os.path.isabs(path) else os.path.abspath(os.path.join(source, path))


class PathTestParameter(TestParameter[Path]):
    """
    A test parameter that should contain a valid path.

    If specified, the parameter can check if the path exists, and if the path is a file or a dir.
    If is_file is set (to either True or False), exists will always be True.

    .. code-block:: python

        inm_venv = PathTestParameter(
            argument="--venv",
            environment_variable="INMANTA_TEST_ENV",
            usage=(
                "Folder in which to place the virtual env for tests (will be shared by all tests). "
                "This options depends on symlink support. This does not work on all windows versions. "
                "On windows 10 you need to run pytest in an admin shell. "
                "Using a fixed virtual environment can speed up running the tests."
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
        default: Optional[Union[Path, DynamicDefault[Path]]] = None,
        key: Optional[str] = None,
        group: Optional[str] = None,
        legacy: Optional["PathTestParameter"] = None,
        is_file: Optional[bool] = None,
        exists: Optional[bool] = None,
        legacy_environment_variable: Optional[str] = None,
    ) -> None:
        self.is_file = is_file
        self.exists = exists if is_file is None else True
        super().__init__(
            argument,
            environment_variable,
            usage,
            default=default,
            key=key,
            group=group,
            legacy=legacy,
            legacy_environment_variable=legacy_environment_variable,
        )

    def validate(self, raw_value: object) -> Path:

        # Use module curdir to allow relative path
        # This is required because wherever the shared_project fixture is used, the cwd
        # will be changed by `Project.set()`, meaning that if the test option is resolved after
        # the fixture is called, the relative path would point to a different place making it way
        # harder to use said option.
        path = Path(
            abspath(str(raw_value), source=pytest_inmanta.plugin.CURDIR)
        ).absolute()

        if self.exists is None:
            # We don't need the file to exist, nothing to check here
            return path

        if path.exists() != self.exists:
            expected = "not " if not self.exists else ""
            actual = "not " if self.exists else ""
            raise ValueError(
                f"The path should {expected}exist but does{actual}: {path}"
            )

        if not self.exists:
            # If the path doesn't exist, it won't be a file not a dir
            return path

        if self.is_file is None:
            # Nothing more to check
            return path

        if path.is_file() != self.is_file:
            expected = "file" if self.is_file else "dir"
            actual = "file" if not self.is_file else "dir"
            raise ValueError(f"Got a {actual} where a {expected} was expected: {path}")

        return path
