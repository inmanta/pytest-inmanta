"""
    Copyright 2020 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

import pytest

from inmanta.ast import ExplicitPluginException


def test_import(project):
    from inmanta_plugins.testmodule import regular_function

    assert regular_function() == "imported"


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

    import inmanta_plugins.testmodule  # noqa: F401, F811

    assert std.pytest_inmanta_side_effect_count == 1


def test_inmanta_plugins_fixture(inmanta_plugins):
    assert inmanta_plugins.testmodule.regular_function() == "imported"
    assert inmanta_plugins.testmodule.submod.submod_loaded is True
    with pytest.raises(
        AttributeError, match="No inmanta module named non_existant_module"
    ):
        inmanta_plugins.non_existant_module


def test_inmanta_plugins_fixture_dynamic(project, inmanta_plugins):
    def dynamic_get_exception():
        return inmanta_plugins.testmodule.get_exception

    def do_assertions():
        assert inmanta_plugins.testmodule.get_exception is dynamic_get_exception()
        assert inmanta_plugins.testmodule.get_exception is project.get_plugin_function(
            "get_exception"
        )
        assert (
            inmanta_plugins.testmodule.get_exception()
            is project.get_plugin_function("get_exception")()
        )
        assert (
            inmanta_plugins.testmodule.get_exception()
            is inmanta_plugins.testmodule.TestException
        )

    do_assertions()
    project.compile("import testmodule")
    do_assertions()


def test_inmanta_plugins_except(project, inmanta_plugins):
    with pytest.raises(ExplicitPluginException) as exception_info:
        project.compile(
            """
    import testmodule

    testmodule::raise_exception()
            """
        )
    assert isinstance(
        exception_info.value.__cause__, inmanta_plugins.testmodule.TestException
    )
    assert (
        project.get_plugin_function("get_exception")()
        is inmanta_plugins.testmodule.TestException
    )
