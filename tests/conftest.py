import pytest
import pytest_inmanta.plugin
import os

pytest_plugins = ["pytester"]

@pytest.fixture(autouse=True)
def set_cwd(testdir):
    pytest_inmanta.plugin.CURDIR =  os.getcwd()