"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""


def test_capture(project):
    marker = "MARKERXXX123678"

    basemodel = f"""
    std::print("{marker}")
    """

    project.compile(basemodel)

    assert marker in project.get_stdout()
