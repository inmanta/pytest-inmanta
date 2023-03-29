"""
    Copyright 2021 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""
import pathlib

import inmanta.agent.handler
import inmanta.config
import inmanta.resources
from inmanta.plugins import plugin


@plugin
def myplugin(x: "int") -> "int":
    return x


@inmanta.resources.resource("testmodulev2::Print", "file", "agent_name")
class PrintResource(inmanta.resources.PurgeableResource):
    fields = (
        "file",
        "content",
    )


@inmanta.agent.handler.provider("testmodulev2::Print", "base")
class PrintProvider(inmanta.agent.handler.CRUDHandler):
    def path(self, resource: inmanta.resources.PurgeableResource) -> pathlib.Path:
        # If the path is absolute, return the absolute path, if it is relative,
        # consider it relative to the agent state dir, and return the absolute
        # path equivalent.
        return pathlib.Path(inmanta.config.state_dir.get(), resource.file)

    def read_resource(
        self,
        ctx: inmanta.agent.handler.HandlerContext,
        resource: inmanta.resources.PurgeableResource,
    ) -> None:
        if not self.path(resource).exists():
            raise inmanta.agent.handler.ResourcePurged()

        resource.content = self.path(resource).read_text()

    def create_resource(
        self,
        ctx: inmanta.agent.handler.HandlerContext,
        resource: inmanta.resources.PurgeableResource,
    ) -> None:
        self.path(resource).parent.mkdir(parents=True, exist_ok=True)
        self.path(resource).write_text(resource.content)

    def update_resource(
        self,
        ctx: inmanta.agent.handler.HandlerContext,
        changes: dict[str, dict[str, object]],
        resource: inmanta.resources.PurgeableResource,
    ) -> None:
        self.path(resource).write_text(resource.content)

    def delete_resource(
        self,
        ctx: inmanta.agent.handler.HandlerContext,
        resource: inmanta.resources.PurgeableResource,
    ) -> None:
        self.path(resource).unlink()
