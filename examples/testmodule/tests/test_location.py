"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0

    This file is used to test --use-module-in-place
"""

def test_location(project):
    basemodel = """
    import testmodule

    testmodule::create_testfile()
    """

    project.compile(basemodel)
