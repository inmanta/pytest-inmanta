"""
Copyright 2018 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""

import pytest

from inmanta import const
from pytest_inmanta.plugin import DeployResultV2, Project


def test_basic_run_v2(project):
    basemodel = """
    import testmodule

    testmodule::Resource(agent="a", name="IT", key="k", value="write")
    testmodule::Fail(agent="a", name="IT", key="k", value="write")
    """

    project.compile(basemodel)

    # Simple resource
    project.deploy_resource_v2("testmodule::Resource")

    # Failure and more assertions
    result = project.deploy_resource_v2(
        "testmodule::Fail", expected_status=const.ResourceState.failed
    )
    result.assert_has_logline("Calling read_resource")
    logline = result.assert_has_logline("Oh no!")
    assert logline.log_level == const.LogLevel.WARNING
    assert "value" in result.changes
    result.assert_consistent_status()

    # capture result, ignore failure
    result: DeployResultV2 = project.deploy_resource_v2(
        "testmodule::Fail", expected_status=None
    )
    result.assert_status(const.ResourceState.failed)
    result.assert_consistent_status()

    with pytest.raises(AssertionError):
        project.deploy_resource_v2("testmodule::Fail")


def test_dryrun(project: Project):
    basemodel = """
    import testmodule

    r = testmodule::Resource(agent="a", name="IT", key="k", value="write")
    """

    project.compile(basemodel)

    result = project.deploy_resource_v2("testmodule::Resource", dry_run=True)

    assert ["value"] == list(result.changes.keys())
    change = result.changes["value"]
    assert change.model_dump() == {"current": "read", "desired": "write"}

    with pytest.raises(AssertionError):
        assert result.assert_no_changes()

    result.assert_consistent_status()
