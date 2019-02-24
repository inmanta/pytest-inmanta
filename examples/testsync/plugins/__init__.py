"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

from inmanta.agent.handler import provider, CRUDHandler, HandlerContext
from inmanta.resources import resource, Resource
from tornado import gen


@resource("testsync::Resource", agent="agent", id_attribute="name")
class ResourceResource(Resource):
    fields = ("name", "agent", "key", "value")


@provider("testsync::Resource", name="resourceprovider")
class ResourceHandler(CRUDHandler):

    def read_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        resource.purged = False
        resource.value = "read"

    def create_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        ctx.set_created()

    @gen.coroutine
    def test_sync(self):
        yield gen.sleep(0.1)
        return 5

    def update_resource(self, ctx: HandlerContext, changes: dict, resource: ResourceResource) -> None:
        a = self.run_sync(self.test_sync)
        assert a == 5
        ctx.set_updated()

    def facts(self, ctx, resource):
        facts = {"fact": "fact"}
        return facts

    def delete_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        ctx.set_purged()
