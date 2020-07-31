"""
    Copyright 2020 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

def test_49_plugin_load_compatibility(project):
    """
        Make sure get_plugin_function is compatible with the compiler's import mechanism
    """
    from inmanta_plugins.testmodule import TestException
    test_exception = project.get_plugin_function("get_exception")()
    assert test_exception is TestException

    project.compile("import testmodule")

    from inmanta_plugins.testmodule import TestException
    assert test_exception is TestException
    assert project.get_plugin_function("get_exception")() is project.get_plugin("get_exception")()


def test_49_plugin_load_side_effects(caplog, project):
    assert caplog.text == "loading module...\n"
