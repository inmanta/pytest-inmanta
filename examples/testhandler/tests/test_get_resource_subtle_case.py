"""
Copyright 2024 Inmanta

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

from pytest_inmanta.plugin import Project


def test_subtle_get_resource(project: Project):
    """
    Ensure that the stricter filtering on get_resource is working as intended on a subtle scenario -> inheritance in the model
    but relying on the same resource / handler pair. Things that need to be checked:
        - Makes sure that the entity type of the resource is matching the one provided in the arguments
        - Only one instance exists in the resources of the project
    """
    # First, let's test the old behaviour: the returned resource has an incorrect type
    project.compile(
        """
    import unittest

    unittest::Resource(name="res", desired_value="x")
    unittest::ResourceA(name="fakeres", desired_value="fakex")
    """
    )

    # will not find anything in normal mode, but will in strict mode
    assert project.get_resource("unittest::Resource", name="fakeres") is None
    resource = project.get_resource(
        "unittest::Resource", strict_mode=True, name="fakeres"
    )
    assert resource is not None
    assert resource.id.entity_type == "unittest::Resource"

    # will not find anything in strict mode, but will in normal mode
    assert (
        project.get_resource("unittest::ResourceA", strict_mode=True, name="fakeres")
        is None
    )
    resource = project.get_resource("unittest::ResourceA", name="fakeres")
    assert resource is not None
    assert resource.id.entity_type == "unittest::Resource"

    # will fail in strict mode, succeed in normal mode
    assert project.get_resource("unittest::Resource") is not None
    with pytest.raises(AssertionError):
        project.get_resource("unittest::Resource", strict_mode=True)

    # And let's make sure that if the resource doesn't exist, `None` is returned
    project.compile(
        """
    import unittest
    """
    )
    assert project.get_resource("unittest::ResourceA", strict_mode=True) is None
