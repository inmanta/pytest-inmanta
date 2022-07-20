"""
    Copyright 2021 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""


def test_compile(project):
    """
    Verify that basic compilation using the project fixture works for v2 modules.
    """
    project.compile("import testmodulev2conflict2")
