"""
    Copyright 2020 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

def test_49_plugin_load_side_effects(project):
    """
        Make sure side effects in the module are only executed once.
    """
    import inmanta_plugins.std as std
    assert hasattr(std, "pytest_inmanta_side_effect_count")
    assert std.pytest_inmanta_side_effect_count == 1
    import inmanta_plugins.testmodule
    assert std.pytest_inmanta_side_effect_count == 1
    project.compile("import testmodule")
    assert std.pytest_inmanta_side_effect_count == 1
    import inmanta_plugins.testmodule
    assert std.pytest_inmanta_side_effect_count == 1
