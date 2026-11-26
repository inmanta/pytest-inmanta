"""
Copyright 2026 Inmanta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact: code@inmanta.com
"""

import graphlib
from collections.abc import Iterable, Mapping, Sequence

from inmanta.data.model import ResourceIdStr
from inmanta.resources import Resource


class DependencyCycleException(Exception):
    """
    Raised when the requires relationships of the resources produced by a compile contain a cycle.
    """

    def __init__(self, cycle: Sequence[ResourceIdStr]) -> None:
        """
        :param cycle: The ids of the resources that form the cycle, in the direction of the requires relationships.
                      The first and the last element are the same resource.
        """
        self.cycle = cycle
        super().__init__(
            f"The requires relationships of the resources contain a cycle: {' -> '.join(cycle)}"
        )

    @classmethod
    def from_core_exception(cls, exception: Exception) -> "DependencyCycleException":
        """
        Create a DependencyCycleException from the DependencyCycleException raised by the exporter of older
        inmanta-core versions.

        :param exception: The exception raised by the exporter of inmanta-core. Its cycle attribute contains the
                          resources of the cycle, in the opposite direction of the requires relationships.
        """
        resource_ids: list[ResourceIdStr] = [
            resource.id.resource_str()
            for resource in reversed(exception.cycle)  # type: ignore[attr-defined]
        ]
        return cls(cycle=[*resource_ids, resource_ids[0]])


class RequiresCycleDetector:
    """
    Detects cycles in a graph of requires relationships between resources.
    """

    def __init__(
        self, requires: Mapping[ResourceIdStr, Iterable[ResourceIdStr]]
    ) -> None:
        """
        :param requires: Maps the id of a resource to the ids of the resources it requires.
        """
        self.requires = requires

    @classmethod
    def from_resources(cls, resources: Iterable[Resource]) -> "RequiresCycleDetector":
        """
        Create a RequiresCycleDetector for the requires relationships of the given resources.

        :param resources: The resources produced by a compile.
        """
        return cls(
            {
                resource.id.resource_str(): [
                    required.resource_str() for required in resource.requires
                ]
                for resource in resources
            }
        )

    def ensure_no_cycle(self) -> None:
        """
        Raise a DependencyCycleException when the requires relationships contain a cycle.
        """
        try:
            graphlib.TopologicalSorter(self.requires).prepare()
        except graphlib.CycleError as e:
            # The TopologicalSorter reports the cycle in the opposite direction of the requires relationships
            raise DependencyCycleException(cycle=list(reversed(e.args[1])))
