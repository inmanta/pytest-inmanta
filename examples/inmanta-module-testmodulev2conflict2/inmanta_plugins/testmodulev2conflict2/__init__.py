"""
Copyright 2021 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""

from inmanta.plugins import plugin


@plugin
def myplugin(x: "int") -> "int":
    return x
