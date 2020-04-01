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
from inmanta import const

from pytest_inmanta.handler import DATA


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


def test_resource_fail_skip(project):
    project.compile("""
    import unittest

    unittest::Resource(name="res", desired_value="x", fail=true)
    """)
    project.deploy_resource("unittest::Resource", status=const.ResourceState.failed)

    project.compile("""
        import unittest

        unittest::Resource(name="res", desired_value="x", skip=true)
        """)
    project.deploy_resource("unittest::Resource", status=const.ResourceState.skipped)


def test_resource_fail_skip_data(project):
    project.compile("""
    import unittest

    unittest::Resource(name="res", desired_value="x")
    """)

    project.deploy_resource("unittest::Resource", status=const.ResourceState.deployed)

    DATA["res"]["skip"] = True
    project.deploy_resource("unittest::Resource", status=const.ResourceState.skipped)

    DATA["res"]["skip"] = False
    DATA["res"]["fail"] = True
    project.deploy_resource("unittest::Resource", status=const.ResourceState.failed)


def test_retrieve_logs(project):

    project.compile("""
    import unittest

    unittest::Resource(name="res", desired_value="x")
    """)
    project.deploy_resource("unittest::Resource")

    assert project.unittest_resource_exists(name="res")
    logs = project.get_last_logs()
    assert len(logs) == 3

    project.dryrun_resource("unittest::Resource")
    logs = project.get_last_logs()
    assert len(logs) == 2


def test_close_cache(project):
    project.compile("""
        import unittest

        unittest::Resource(name="res", desired_value="x")
        """)

    project.deploy_resource("unittest::Resource")
    res = project.get_resource("unittest::Resource")
    handler = project.get_handler(res, False)
    project.finalize_handler(handler)
    versions = handler.cache.counterforVersion.keys()
    assert len(versions) == 0
