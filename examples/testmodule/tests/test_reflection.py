"""
Copyright 2018 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""

import pytest

import inmanta


def test_model_inspection(project):
    basemodel = """
    import testmodule

    r = testmodule::Resource(agent="a", name="r", key="k", value="write")
    r2 = testmodule::Resource(agent="a", name="r2", key="k", value="write")

    entity Other:
        string name
    end

    implement Other using std::none

    Other.resource [0:] -- testmodule::Resource
    Other.optional [0:1] -- testmodule::Resource

    a = Other(name="a")
    b = Other(name="b")

    a.resource = r
    a.resource = r2
    """

    project.compile(basemodel)

    all = project.get_instances()

    named = {a.name: a for a in all}

    ar = named["a"].resource
    assert len(ar) == 2
    namesinar = [a.name for a in ar]
    assert sorted(namesinar) == ["r", "r2"]

    with pytest.raises(inmanta.ast.NotFoundException):
        named["a"].xx

    assert not named["b"].resource

    with pytest.raises(inmanta.ast.OptionalValueException):
        named["a"].optional
