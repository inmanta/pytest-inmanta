"""
    Copyright 2023 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""
import pathlib

import pytest_inmanta.plugin


def test_compile(
    project: pytest_inmanta.plugin.Project,
    inmanta_state_dir: str,
    set_inmanta_state_dir: None,
) -> None:
    """
    Verify that basic compilation using the project fixture works for v2 modules.
    """
    model = """
        import testmodulev2

        testmodulev2::Print(
            file="test.txt",
            content="aha",
        )
    """.strip(
        "\n"
    )

    project.compile(model, no_dedent=False)
    assert project.dryrun_resource("testmodulev2::Print")
    assert project.deploy_resource("testmodulev2::Print")
    assert not project.dryrun_resource("testmodulev2::Print")

    assert pathlib.Path(inmanta_state_dir, "test.txt").read_text() == "aha"
