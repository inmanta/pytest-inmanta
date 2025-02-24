from inmanta.agent.handler import LoggerABC
from inmanta.plugins import plugin
from inmanta.references import Reference, reference
from inmanta.resources import ManagedResource, PurgeableResource, resource


@reference("refs::String")
class StringReference(Reference[str]):
    """A dummy reference to a string"""

    def __init__(self, name: str | Reference[str]) -> None:
        """
        :param name: The name of the environment variable.
        """
        super().__init__()
        self.name = name

    def resolve(self, logger: LoggerABC) -> str:
        """Resolve the reference"""
        return self.resolve_other(self.name, logger)

    def __str__(self) -> str:
        return "StringReference"


@plugin
def create_string_reference(name: Reference[str] | str) -> Reference[str]:
    return StringReference(name=name)


@resource("refs::NullResource", agent="agentname", id_attribute="name")
class Null(ManagedResource, PurgeableResource):
    fields = ("name", "agentname", "fail", "value")
