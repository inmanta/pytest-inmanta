"""
    Copyright 2020 Inmanta
    Contact: code@inmanta.com
    License: Apache 2.0
"""
from os import path

from inmanta import module


def test_multiple_paths(project):
    project_inmanta = module.Project(project._test_project_dir)
    children: List[module.ModuleRepo] = (
        project_inmanta.module_source_v1.remote_repo.children
        if hasattr(project_inmanta, "module_source_v1")
        else project_inmanta.externalResolver.children
    )
    module_repo_urls = [repo.baseurl for repo in children]
    assert "https://github.com/inmanta2/" in module_repo_urls
    assert "https://github.com/inmanta/" in module_repo_urls
    with open(path.join(project._test_project_dir, "project.yml"), "r") as project_file:
        content = project_file.read()
        assert (
            "repo: ['https://github.com/inmanta2/', 'https://github.com/inmanta/']"
            in content
        )
