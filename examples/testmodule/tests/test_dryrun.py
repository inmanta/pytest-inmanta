"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""
from inmanta.data.model import AttributeStateChange


def test_dryrun(project):
    basemodel = """
    import testmodule

    r = testmodule::Resource(agent="a", name="IT", key="k", value="write")
    """

    project.compile(basemodel)

    changes = project.dryrun_resource("testmodule::Resource")
    assert ["value"] == list(changes.keys())
    change = changes["value"]
    # change in type in iso7
    if isinstance(change, AttributeStateChange):
        change = change.model_dump()
    assert change == {"current": "read", "desired": "write"}
