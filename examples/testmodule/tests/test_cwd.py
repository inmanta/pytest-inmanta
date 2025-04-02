"""
Copyright 2022 Inmanta
Contact: code@inmanta.com
License: Apache 2.0
"""

import os

CURDIR = os.getcwd()
test_case_one_ran = False


def test_case_one(project) -> None:
    """
    Verify that the project fixture has changed the CWD.
    """
    global test_case_one_ran
    test_case_one_ran = True
    assert os.getcwd() != CURDIR


def test_case_two() -> None:
    """
    Verify that project fixture resets the CWD in the cleanup stage.
    """
    assert test_case_one_ran, "test_case_one should execute fore test_case_two"
    assert os.getcwd() == CURDIR
