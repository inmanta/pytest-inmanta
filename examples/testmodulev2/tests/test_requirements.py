"""
    Copyright 2022 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""

import pytest
from pkg_resources import Requirement

@pytest.fixture
def myproject_with_lorem(project):
    project.set_requirements([Requirement.parse("lorem")])
    yield project


def test_with_lorem(myproject_with_lorem):
    with pytest.raises(ImportError):
        # assert that lorem isn't installed because it would make the test meaningless
        import lorem
    myproject_with_lorem.compile("")
    import lorem


# TODO: this fails because the compiler venv is shared between instances of the project fixture. Would the overhead be
#   acceptable if we just delete it in pytest_inmanta.Project.clean()? If not, the custom fixture will have to use the
#   project_factory as parent
def test_without_lorem(project):
    project.compile("")
    with pytest.raises(ImportError):
        # assert that lorem is only installed with the custom project fixture
        import lorem
