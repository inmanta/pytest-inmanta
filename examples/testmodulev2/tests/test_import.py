"""
    Copyright 2021 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

# verify that top-level imports are supported
from inmanta_plugins import std, testmodulev2


def test_dynamic_import(project):
    from inmanta_plugins import testmodulev2 as testmodulev2_dynamic
    from inmanta_plugins import std as std_dynamic

    assert testmodulev2_dynamic is testmodulev2
    assert std_dynamic is std

    project.compile("import testmodulev2")

    from inmanta_plugins import testmodulev2 as testmodulev2_dynamic
    from inmanta_plugins import std as std_dynamic

    assert testmodulev2_dynamic is testmodulev2
    assert std_dynamic is std


def test_inmanta_plugins_fixture(inmanta_plugins):
    assert inmanta_plugins.testmodulev2 is testmodulev2
    assert inmanta_plugins.std is std


def test_get_plugin(project, inmanta_plugins):
    assert project.get_plugin_function("myplugin") is testmodulev2.myplugin
    project.compile("import testmodulev2")
    assert project.get_plugin_function("myplugin") is testmodulev2.myplugin
