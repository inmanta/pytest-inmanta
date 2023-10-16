"""
    Copyright 2020 Inmanta

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


def test_ignore_resource(project):
    """
    Ensure that instances of the unittest::IgnoreResource resources are not exported.
    These resources raise an IgnoreResourceException on export.
    """
    project.compile(
        """
    import unittest

    unittest::Resource(name="res", desired_value="x")
    unittest::IgnoreResource(name="res_ignore", desired_value="y")
    unittest::IgnoreResourceInId(name="res_ignore_2", desired_value="z")
    """
    )

    assert project.get_resource("unittest::Resource") is not None
    assert project.get_resource("unittest::IgnoreResource") is None
    assert project.get_resource("unittest::IgnoreResourceInId") is None
