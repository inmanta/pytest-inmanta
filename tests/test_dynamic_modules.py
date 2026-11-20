"""
Copyright 2026 Inmanta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact: code@inmanta.com
"""

import importlib
import importlib.metadata
import pathlib
import shutil
import sys
import typing

import pytest

from inmanta import module
from pytest_inmanta import dynamic_modules


@pytest.fixture
def finder(
    monkeypatch: pytest.MonkeyPatch,
) -> typing.Iterator[dynamic_modules.DynamicModuleFinder]:
    """
    A fresh finder whose changes to sys.meta_path and sys.modules are undone after the test.
    """
    monkeypatch.setattr(sys, "meta_path", list(sys.meta_path))
    modules_before = set(sys.modules)
    yield dynamic_modules.DynamicModuleFinder()
    for name in set(sys.modules) - modules_before:
        if name.startswith("inmanta_plugins."):
            del sys.modules[name]


def create(
    finder: dynamic_modules.DynamicModuleFinder,
    project_dir: pathlib.Path,
    name: str,
) -> pathlib.Path:
    module_dir = project_dir / "libs" / name
    module_dir.parent.mkdir(parents=True, exist_ok=True)
    dynamic_modules.write_module(str(module_dir), name, "", "X = 1")
    finder.install(name, str(module_dir))
    return module_dir


def is_importable(name: str) -> bool:
    sys.modules.pop(f"inmanta_plugins.{name}", None)
    try:
        importlib.import_module(f"inmanta_plugins.{name}")
    except ImportError:
        return False
    return True


def test_module_is_importable_from_its_tree(finder, tmp_path) -> None:
    """
    A dynamic module's plugin package and its submodules are imported from its tree in libs/, without installing it.
    """
    finder.use_project(str(tmp_path / "project"))
    module_dir = create(finder, tmp_path / "project", "dynimport")
    (module_dir / "inmanta_plugins" / "dynimport" / "sub.py").write_text("Y = 2")

    assert is_importable("dynimport")
    module = sys.modules["inmanta_plugins.dynimport"]
    assert module.__file__ == str(
        module_dir / "inmanta_plugins" / "dynimport" / "__init__.py"
    )
    assert importlib.import_module("inmanta_plugins.dynimport.sub").Y == 2
    with pytest.raises(importlib.metadata.PackageNotFoundError):
        importlib.metadata.distribution("inmanta-module-dynimport")


def test_project_change_drops_other_projects_modules(finder, tmp_path) -> None:
    """
    Switching to another test project drops the dynamic modules of the previous one.
    """
    project1 = tmp_path / "project1"
    finder.use_project(str(project1))
    create(finder, project1, "dynproject")
    assert is_importable("dynproject")

    project2 = tmp_path / "project2"
    finder.use_project(str(project2))
    # The previous project's tree is still on disk, but its module is no longer visible
    assert (project1 / "libs" / "dynproject").is_dir()
    assert not is_importable("dynproject")

    create(finder, project2, "dynproject")
    assert is_importable("dynproject")


def test_removed_module_is_not_importable(finder, tmp_path) -> None:
    """
    A dynamic module whose tree was removed can't be imported, and prune drops it.
    """
    finder.use_project(str(tmp_path / "project"))
    module_dir = create(finder, tmp_path / "project", "dynprune")
    shutil.rmtree(module_dir)
    assert not is_importable("dynprune")

    finder.prune()
    create(finder, tmp_path / "project", "dynprune")
    assert is_importable("dynprune")


def test_finder_returns_to_meta_path(finder, tmp_path) -> None:
    """
    The finder puts itself back at the front of sys.meta_path if something removed it.
    """
    finder.use_project(str(tmp_path / "project"))
    create(finder, tmp_path / "project", "dynmetapath")
    sys.meta_path.remove(finder)
    assert not is_importable("dynmetapath")

    finder.prune()
    assert sys.meta_path[0] is finder
    assert is_importable("dynmetapath")


def test_installed_module_name_is_refused(finder, tmp_path) -> None:
    """
    A dynamic module can't take the name of an installed module.
    """
    installed = next(
        dist.metadata["Name"]
        for dist in importlib.metadata.distributions()
        if dist.metadata["Name"].startswith("inmanta-module-")
    )
    name = installed[len("inmanta-module-") :].replace("-", "_")
    finder.use_project(str(tmp_path / "project"))
    with pytest.raises(
        Exception, match="can't share its name with an installed module"
    ):
        create(finder, tmp_path / "project", name)


def test_module_name_with_underscore(tmp_path) -> None:
    """
    A dynamic module whose name contains an underscore has valid V2 metadata.
    """
    module_dir = tmp_path / "libs" / "dyn_underscore"
    module_dir.parent.mkdir(parents=True)
    dynamic_modules.write_module(str(module_dir), "dyn_underscore", "", "")
    loaded = module.Module.from_path(str(module_dir))
    assert isinstance(loaded, module.ModuleV2)
    assert loaded.name == "dyn_underscore"
