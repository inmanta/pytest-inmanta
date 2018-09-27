# pytest-inmanta

A pytest plugin to test inmanta modules

## Installation

```bash
pip install pytest-inmanta
```

## Usage

This plugin provides a test fixture that can compile, export and deploy code without running an actual inmanta server.

```python
def test_compile(project):
    """
        Test compiling a simple model that uses std
    """
    project.compile("""
host = std::Host(name="server", os=std::linux)
file = std::ConfigFile(host=host, path="/tmp/test", content="1234")
        """)
```

The fixture also provides access to the model internals

```python
    assert len(project.types["std::Host"].get_all_instances()) == 1
```

To the exported resources

```python
    f = project.get_resource("std::ConfigFile")
    assert f.permissions == 644
```

To compiler output and mock filesystem

```python
def test_template(project):
    """
        Test the evaluation of a template
    """
    project.add_mock_file("templates", "test.tmpl", "{{ value }}")
    project.compile("""import unittest
value = "1234"
std::print(std::template("unittest/test.tmpl"))
    """)

    assert project.get_stdout() == "1234\n"
```

And allows deploy

```python
    project.deploy_resource("std::ConfigFile")
```