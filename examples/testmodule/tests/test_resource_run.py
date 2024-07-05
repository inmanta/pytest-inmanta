"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

from inmanta.ast import Namespace


def test_basic_run(project):
    basemodel = """
    import testmodule

    r = testmodule::Resource(agent="a", name="IT", key="k", value="write")
    """

    project.compile(basemodel)
    project.deploy_resource("testmodule::Resource")

    scopes: Namespace = project.get_root_scope()
    assert "testmodule" in [str(x) for x in scopes.children()]
