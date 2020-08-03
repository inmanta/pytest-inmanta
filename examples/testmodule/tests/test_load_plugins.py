"""
    Copyright 2020 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

import inmanta

def test_49_plugin_load_compatibility(project):
    """
        Make sure get_plugin_function is compatible with the compiler's import mechanism
    """
    from inmanta_plugins.testmodule import TestException
    test_exception = project.get_plugin_function("get_exception")()
    assert test_exception is TestException

    project.compile("import testmodule")

    from inmanta_plugins.testmodule import TestException as TestException2
    test_exception2 = project.get_plugin_function("get_exception")()
    assert test_exception2 is TestException2
    assert TestException is TestException2


def test_49_plugin_load_side_effects(project):
    """
        Make sure side effects in the module are only executed once.
    """
    assert hasattr(inmanta, "pytest_inmanta_side_effect_count")
    assert inmanta.pytest_inmanta_side_effect_count == 1
    import inmanta_plugins.testmodule
    assert inmanta.pytest_inmanta_side_effect_count == 1
    project.compile("import testmodule")
    assert inmanta.pytest_inmanta_side_effect_count == 1
    import inmanta_plugins.testmodule
    assert inmanta.pytest_inmanta_side_effect_count == 1
