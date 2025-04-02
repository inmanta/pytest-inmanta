"""
Copyright 2018 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""


def test_dryrun(project):
    basemodel = """
    import testmodule

    r = testmodule::Resource(agent="a", name="IT", key="k", value="write")
    """

    project.compile(basemodel)

    changes = project.dryrun_resource("testmodule::Resource")
    assert ["value"] == list(changes.keys())
    change = changes["value"]
    assert change.model_dump() == {"current": "read", "desired": "write"}
