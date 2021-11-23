"""
    Copyright 2021 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""


def test_module_state(project, inmanta_plugins) -> None:
    """
    Verify that state on Python module objects does not carry accross compiles if an appropriate cleanup hook is defined.
    """
    assert len(inmanta_plugins.testmodule.MODULE_CACHE) == 0
    inmanta_plugins.testmodule.MODULE_CACHE.add(1)
    assert 1 in inmanta_plugins.testmodule.MODULE_CACHE

    project.compile("import testmodule")

    assert len(inmanta_plugins.testmodule.MODULE_CACHE) == 0


def test_module_state_advanced(project, inmanta_plugins) -> None:
    """
    Verify that
        - cleanup hooks on submodules get called as well
        - if more than one cleanup hook is defined, all are called
    """
    assert len(inmanta_plugins.testmodule.submod.MODULE_CACHE_ONE) == 0
    assert len(inmanta_plugins.testmodule.submod.MODULE_CACHE_TWO) == 0
    inmanta_plugins.testmodule.submod.MODULE_CACHE_ONE.add(1)
    inmanta_plugins.testmodule.submod.MODULE_CACHE_TWO.add(2)
    assert 1 in inmanta_plugins.testmodule.submod.MODULE_CACHE_ONE
    assert 2 in inmanta_plugins.testmodule.submod.MODULE_CACHE_TWO

    project.compile("import testmodule")

    assert len(inmanta_plugins.testmodule.submod.MODULE_CACHE_ONE) == 0
    assert len(inmanta_plugins.testmodule.submod.MODULE_CACHE_TWO) == 0
