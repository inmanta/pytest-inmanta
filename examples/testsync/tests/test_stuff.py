"""
Copyright 2018 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""


def test_basic_run(project):
    basemodel = """
    import testsync

    r = testsync::Resource(agent="a", name="IT", key="k", value="write")
    """

    project.compile(basemodel)

    project.deploy_resource("testsync::Resource")
