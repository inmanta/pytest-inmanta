"""
    Copyright 2021 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

import os

from inmanta import config


def test_compile(project):
    """
    Verify that basic compilation using the project fixture works for v2 modules.
    """
    project.compile("import testmodulev2")

    # Verify that the state dir is not /var/lib/inmanta and is writable
    state_dir = config.state_dir.get()
    assert state_dir != "/var/lib/inmanta"
    with open(os.path.join(state_dir, "test.txt"), "w+"):
        pass
