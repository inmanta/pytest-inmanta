"""
Copyright 2026 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""

from typing import Optional

import pytest

from pytest_inmanta.requires_cycle import DependencyCycleException


def get_resource_id(name: str) -> str:
    """
    Return the id of the testmodule::Resource with the given name.
    """
    return f"testmodule::Resource[a,name={name}]"


@pytest.mark.parametrize(
    "requires, expected_cycle",
    [
        # A resource that requires itself
        ({"r1": ["r1"]}, ["r1"]),
        # A cycle of three resources and a resource that requires a resource in the cycle
        ({"r1": ["r2"], "r2": ["r3"], "r3": ["r1"], "r4": ["r1"]}, ["r1", "r2", "r3"]),
        # A diamond doesn't contain a cycle
        ({"r1": ["r2", "r3"], "r2": ["r4"], "r3": ["r4"], "r4": []}, None),
    ],
)
def test_requires_cycle(
    project, requires: dict[str, list[str]], expected_cycle: Optional[list[str]]
) -> None:
    """
    Ensure that a compile raises a DependencyCycleException that reports the cycle in the
    requires relationships of the resources, if the requires relationships contain a cycle.

    :param requires: Maps the name of a resource to the names of the resources it requires.
    :param expected_cycle: The names of the resources in the cycle, in the direction of the
                           requires relationships, or None if the model doesn't contain a cycle.
    """
    model = "import testmodule\n"
    for name in requires:
        model += f'{name} = testmodule::Resource(agent="a", name="{name}", key="k", value="v")\n'
    for name, required_names in requires.items():
        for required_name in required_names:
            model += f"{name}.requires += {required_name}\n"

    if expected_cycle is None:
        project.compile(model)
        assert len(project.resources) == len(requires)
        return

    with pytest.raises(DependencyCycleException) as exc_info:
        project.compile(model)

    reported_cycle = exc_info.value.cycle
    # The first and the last resource of the reported cycle are the same
    assert reported_cycle[0] == reported_cycle[-1]
    # The reported cycle can start at any of the resources of the cycle
    expected_resource_ids = [get_resource_id(name) for name in expected_cycle]
    start_index = expected_resource_ids.index(reported_cycle[0])
    assert (
        reported_cycle[:-1]
        == expected_resource_ids[start_index:] + expected_resource_ids[:start_index]
    )
