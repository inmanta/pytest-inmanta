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
import os


def test_unittest_reload(project, inmanta_plugins) -> None:
    """
    Verify that the unittest module's Python files get reloaded correctly for each compile.
    """
    project.add_mock_file("plugins", "submod.py", "X = 0")
    project.compile("import unittest")
    assert inmanta_plugins.unittest.submod.X == 0
    project.add_mock_file("plugins", "submod.py", "X = 42")
    project.compile("import unittest")
    assert inmanta_plugins.unittest.submod.X == 42


def test_create_module_reload(project, inmanta_plugins) -> None:
    """
    Verify that changes to dynamic modules (created with project.create_module) get reloaded correctly for each compile.
    """
    project.create_module("mycustommodule", "", "X = 0")
    project.compile("import mycustommodule")
    assert inmanta_plugins.mycustommodule.X == 0
    with open(
        os.path.join(
            project._test_project_dir,
            "libs",
            "mycustommodule",
            "plugins",
            "__init__.py",
        ),
        "w",
    ) as fd:
        fd.write("X = 42")
    project.compile("import mycustommodule")
    assert inmanta_plugins.mycustommodule.X == 42
