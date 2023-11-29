"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""
import os
from pathlib import Path

import inmanta_plugins.std as std
from inmanta.agent.handler import CRUDHandler, HandlerContext, provider
from inmanta.plugins import PluginException, plugin
from inmanta.resources import PurgeableResource, resource

# perform side effect on another module in the inmanta_plugins package
# to make sure it is only executed once (test_49_plugin_load_side_effects)
if not hasattr(std, "pytest_inmanta_side_effect_count"):
    std.pytest_inmanta_side_effect_count = 0
std.pytest_inmanta_side_effect_count += 1


@resource("testmodule::Resource", agent="agent", id_attribute="name")
@resource("testmodule::BadLog", agent="agent", id_attribute="name")
@resource("testmodule::ResourceBadIdAttribute", agent="agent", id_attribute="id")
@resource("testmodule::Fail", agent="agent", id_attribute="name")
class ResourceResource(PurgeableResource):
    fields = ("name", "agent", "key", "value")


@provider("testmodule::Resource", name="resourceprovider")
class ResourceHandler(CRUDHandler):
    def read_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        resource.purged = False
        resource.value = "read"

    def create_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        ctx.set_created()

    def update_resource(
        self, ctx: HandlerContext, changes: dict, resource: ResourceResource
    ) -> None:
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
        ctx.warning("argument can not be serialized", argument={"a": "b"}.values())


@provider("testmodule::Fail", name="fail")
class ResourceHandler(ResourceHandler):
    def read_resource(self, ctx: HandlerContext, resource: ResourceResource) -> None:
        resource.purged = False
        resource.value = "read"

    def update_resource(
        self, ctx: HandlerContext, changes: dict, resource: ResourceResource
    ) -> None:
        ctx.warning("Oh no!")
        raise Exception()


@plugin
def create_testfile():
    Path(os.path.realpath(__file__)).parent.parent.joinpath("testfile").touch()


def regular_function():
    return "imported"


class TestException(PluginException):
    pass


@plugin
def get_exception():
    return TestException


@plugin
def raise_exception():
    raise TestException("my exception")


MODULE_CACHE = set()


def inmanta_reset_state() -> None:
    global MODULE_CACHE
    MODULE_CACHE = set()
