"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

def test_badlog_run(project):
    basemodel = """
    import testmodule

    r = testmodule::BadLog(agent="a", name="IT", key="k", value="write")
    """

    project.compile(basemodel)

    project.deploy_resource("testmodule::BadLog")