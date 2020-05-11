"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""
import os
from pathlib import Path


from inmanta.agent.handler import provider, CRUDHandler, HandlerContext
from inmanta.resources import resource, PurgeableResource
from inmanta.plugins import plugin


@resource("testmodule::Resource", agent="agent", id_attribute="name")
@resource("testmodule::BadLog", agent="agent", id_attribute="name")
class ResourceResource(PurgeableResource):
    fields = ("name", "agent", "key", "value")


@provider("testmodule::Resource", name="resourceprovider")
class ResourceHandler(CRUDHandler):
    def read_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        resource.purged = False
        resource.value = "read"

    def create_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        ctx.set_created()

    def update_resource(self, ctx: HandlerContext, changes: dict, resource: ResourceResource) -> None:
        ctx.set_updated()

    def facts(self, ctx, resource):
        facts = {"fact": "fact"}
        return facts

    def delete_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        ctx.set_purged()


@provider("testmodule::BadLog", name="BadLog")
class ResourceHandler(ResourceHandler):
    def read_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        resource.purged = False
        resource.value = "read"
        ctx.warning("argument can not be serialized", argument={"a":"b"}.values())


@plugin
def create_testfile():
    Path(os.path.realpath(__file__)).parent.parent.joinpath("testfile").touch()


def regular_function():
    return "imported"
