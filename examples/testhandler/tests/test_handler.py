"""
    Copyright 2019 Inmanta

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
import pytest


def test_resource(project):
    assert not project.unittest_resource_exists(name="res")

    with pytest.raises(KeyError):
        project.unittest_resource_get(name="res")

    project.compile("""
    import unittest

    unittest::Resource(name="res", desired_value="x")
    """)
    project.deploy_resource("unittest::Resource")

    assert project.unittest_resource_exists(name="res")
    value = project.unittest_resource_get(name="res")
    assert value["desired_value"] == "x"

    project.compile("""
    import unittest

    unittest::Resource(name="res", desired_value="y")
    """)
    project.deploy_resource("unittest::Resource")
    value = project.unittest_resource_get(name="res")
    assert value["desired_value"] == "y"

    project.compile("""
        import unittest

        unittest::Resource(name="res", desired_value="y", purged=true)
        """)
    project.deploy_resource("unittest::Resource")
    assert not project.unittest_resource_exists(name="res")