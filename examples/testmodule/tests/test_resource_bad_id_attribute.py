"""
    Copyright 2023 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""


def test_bad_id_attribute(project, caplog):
    basemodel = """
    import testmodule

    r = testmodule::ResourceBadIdAttribute(agent="a", name="IT", key="k", value="write", id="test")
    """
    project.compile(basemodel)
