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


# TODO: generalize to any module created with create_module?
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
