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

import pytest

from inmanta.const import ResourceState
from pytest_inmanta.handler import DATA


def test_full_deploy(project):
    project.compile("""
        import unittest

        r1 = unittest::Resource(name="first", desired_value="x", requires=ac1)
        r2 = unittest::Resource(name="second", desired_value="x", requires = r1)
        r3 = unittest::Resource(name="third", desired_value="x", requires = r2)
        unittest::Resource(name="first_to", desired_value="x")

        rs = unittest::Resource(name="r_skip", desired_value="x")
        rf = unittest::Resource(name="r_fail", desired_value="x")
        unittest::Resource(name="skip_to", desired_value="x", requires=[rs,rf])

        ac1 = std::AgentConfig(agentname="test", autostart=true)
        """)

    results = project.deploy_all()
    results.assert_all(ResourceState.deployed)

    DATA["r_skip"]["skip"] = True
    DATA["r_fail"]["fail"] = True

    results = project.deploy_all()

    # We get an error when matching multiple when using `get_context_for`
    with pytest.raises(LookupError):
        results.get_context_for("unittest::Resource")

    # This returns all of them
    assert len(results.get_contexts_for("unittest::Resource", desired_value="x")) == 7

    assert (
        results.get_context_for("unittest::Resource", name="first").status
        == ResourceState.deployed
    )
    assert (
        results.get_context_for("unittest::Resource", name="r_skip").status
        == ResourceState.skipped
    )
    assert (
        results.get_context_for("unittest::Resource", name="skip_to").status
        == ResourceState.skipped
    )
    assert (
        results.get_context_for("unittest::Resource", name="r_fail").status
        == ResourceState.failed
    )
