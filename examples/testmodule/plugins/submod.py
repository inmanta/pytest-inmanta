"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

submod_loaded: bool = True


MODULE_CACHE_ONE = set()
MODULE_CACHE_TWO = set()


def inmanta_reset_state_one() -> None:
    global MODULE_CACHE_ONE
    MODULE_CACHE_ONE = set()


def inmanta_reset_state_two() -> None:
    global MODULE_CACHE_TWO
    MODULE_CACHE_TWO = set()
