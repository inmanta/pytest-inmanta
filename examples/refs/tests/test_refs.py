"""
Copyright 2025 Inmanta

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

import inmanta

def test_refs(project):
    project.compile(
        """
    import refs

    ref = refs::create_string_reference(name="test")
    refs::NullResource(name="T1",agentname="a1", value=ref)
    """
    )

    the_resource = project.get_resource("refs::NullResource")
    # After compile, references are None
    assert the_resource.value is None
    project.resolve_references(the_resource)
    # After resolving, they get their final value
    assert the_resource.value == "test"

    # The copy stored in the project fixture is not updated!
    assert project.get_resource("refs::NullResource").value is None

def test_skipped_refs(project):
    project.compile(
        """
    import refs

    ref = refs::create_skip_reference()
    refs::NullResource(name="T1",agentname="a1", value=ref)
    """
    )

    the_resource = project.get_resource("refs::NullResource")
    # After compile, references are None
    assert the_resource.value is None
    assert project.deploy_resource(
        "refs::NullResource", status=inmanta.const.ResourceState.skipped
    )
