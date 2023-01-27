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
import pytest

from inmanta import const


def test_dryrun(project):
    project.compile(
        """
    import unittest

    unittest::Resource(name="res", desired_value="x")
    """
    )
    project.dryrun_resource("unittest::Resource", status=const.ResourceState.dry)


def test_dryrun_fail_skip(project):
    project.compile(
        """
    import unittest

    unittest::Resource(name="res", desired_value="x", fail=true)
    """
    )
    project.dryrun_resource("unittest::Resource", status=const.ResourceState.failed)

    project.compile(
        """
        import unittest

        unittest::Resource(name="res", desired_value="x", skip=true)
        """
    )
    project.dryrun_resource("unittest::Resource", status=const.ResourceState.skipped)


def test_dryrun_all(project):
    project.compile(
        """
    import unittest

    unittest::Resource(name="res", desired_value="x")
    unittest::Resource(name="res2", desired_value="y")
    unittest::Resource(name="res3", desired_value="z")
    """
    )
    result = project.dryrun_all()
    ctx = result.get_context_for("unittest::Resource", name="res")
    assert ctx.resource.desired_value == "x"

    ctx = result.get_context_for("unittest::Resource", name="res2")
    assert ctx.resource.desired_value == "y"

    ctx = result.get_context_for("unittest::Resource", name="res3")
    assert ctx.resource.desired_value == "z"


def test_failures_in_dryrun_all(project):
    project.compile(
        """
    import unittest

    unittest::Resource(name="res", desired_value="x")
    unittest::Resource(name="res2", desired_value="y", fail=true)
    unittest::Resource(name="res3", desired_value="z")
    """
    )
    result = project.dryrun_all()
    with pytest.raises(AssertionError, match="has status failed, expected dry"):
        result.assert_all(const.ResourceState.dry)


def test_dryrun_and_deploy_all(project):
    project.compile(
        """
    import unittest

    unittest::Resource(name="res", desired_value="x")
    unittest::Resource(name="res2", desired_value="y")
    unittest::Resource(name="res3", desired_value="z")
    """
    )
    project.dryrun_and_deploy_all(assert_create_or_delete=True)


def test_failures_in_dryrun_and_deploy_all(project):
    project.compile(
        """
    import unittest

    unittest::Resource(name="res", desired_value="x")
    unittest::Resource(name="res2", desired_value="y", fail=true)
    unittest::Resource(name="res3", desired_value="z")
    """
    )
    with pytest.raises(AssertionError, match="has status failed, expected dry"):
        project.dryrun_and_deploy_all(assert_create_or_delete=True)
