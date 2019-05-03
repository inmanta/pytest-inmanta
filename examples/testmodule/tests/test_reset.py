"""
    Copyright 2018 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""


def test_reset(project):
    assert len(project._facts) == 0
    project.add_fact("abcd","xxx","yyy")


def test_reset2(project):
    assert len(project._facts) == 0
    project.add_fact("abcd","xxx","yyy")