"""
Copyright 2019 Inmanta

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

import typing

from inmanta import resources
from inmanta.agent import handler
from pytest_inmanta.handler import DATA

KEY_PREFIX = "unittest_"


@resources.resource("unittest::Resource", id_attribute="name", agent="agent")
class Resource(resources.PurgeableResource):
    fields = ("name", "desired_value", "skip", "fail", "fail_deploy", "wrong_diff")


@handler.provider("unittest::Resource", name="test")
class ResourceHandler(handler.CRUDHandler):
    def read_resource(
        self, ctx: handler.HandlerContext, resource: resources.PurgeableResource
    ) -> None:
        ctx.info(
            "Resource fail %(fail)s fails deploy %(fail_deploy)s skip %(skip)s",
            fail=resource.fail,
            fail_deploy=resource.fail_deploy,
            skip=resource.skip,
        )

        if resource.skip:
            raise handler.SkipResource()

        if resource.name in DATA:
            ops = DATA[resource.name]

            if ops.get("skip", False):
                raise handler.SkipResource()

            if ops.get("fail", False):
                raise handler.InvalidOperation()

        if resource.fail:
            raise handler.InvalidOperation()

        if resource.fail_deploy and not ctx.is_dry_run():
            raise handler.InvalidOperation()

        if resource.name not in DATA:
            raise handler.ResourcePurged()

        resource.desired_value = DATA[resource.name]["desired_value"]

    def create_resource(
        self, ctx: handler.HandlerContext, resource: resources.PurgeableResource
    ) -> None:
        DATA[resource.name] = {}
        DATA[resource.name]["desired_value"] = resource.desired_value

        ctx.set_created()

    def delete_resource(
        self, ctx: handler.HandlerContext, resource: resources.PurgeableResource
    ) -> None:
        del DATA[resource.name]

        ctx.set_purged()

    def update_resource(
        self,
        ctx: handler.HandlerContext,
        changes: dict,
        resource: resources.PurgeableResource,
    ) -> None:
        DATA[resource.name]["desired_value"] = resource.desired_value

        ctx.set_updated()

    def calculate_diff(
        self,
        ctx: handler.HandlerContext,
        current: resources.Resource,
        desired: resources.Resource,
    ) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        if current.wrong_diff:
            return {"desired_value": {"current": "x", "desired": "y"}}
        return super().calculate_diff(ctx, current, desired)


@resources.resource("unittest::IgnoreResource", id_attribute="name", agent="agent")
class IgnoreResource(resources.PurgeableResource):
    fields = ("name", "desired_value")

    @staticmethod
    def get_desired_value(exporter, resource):
        raise resources.IgnoreResourceException()


@handler.provider("unittest::IgnoreResource", name="ignore")
@handler.provider("unittest::IgnoreResourceInIdAttr", name="ignore")
class IgnoreResourceHandler(handler.CRUDHandler):
    pass


@resources.resource(
    "unittest::IgnoreResourceInIdAttr", id_attribute="name", agent="agent"
)
class IgnoreResourceInIdAttr(resources.PurgeableResource):
    fields = ("name", "desired_value")

    @staticmethod
    def get_name(exporter, resource):
        raise resources.IgnoreResourceException()
