"""
Copyright 2026 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""

from inmanta.plugins import plugin


@plugin
def double(x: "int") -> "int":
    return 2 * x
