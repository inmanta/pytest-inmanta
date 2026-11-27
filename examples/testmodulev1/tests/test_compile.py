"""
Copyright 2026 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""


def test_compile(project) -> None:
    project.compile("import testmodulev1")
    assert project.get_plugin_function("double")(4) == 8
