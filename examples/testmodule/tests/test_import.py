"""
    Copyright 2020 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""


def test_import(project):
    project.load()
    from inmanta_plugins.testmodule import regular_function

    assert regular_function() == "imported"
