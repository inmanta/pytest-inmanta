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
    assert len(project.get_instances("std::Host")) == 1
    assert project.get_instances("std::Host")[0].name == "server"
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

And dryrun

```python
    changes = project.dryrun_resource("testmodule::Resource")
    assert changes == {"value": {'current': 'read', 'desired': 'write'}}
```

## Testing plugins

Take the following plugin as an example:

```python
    # <module-name>/plugins/__init__.py

    from inmanta.plugins import plugin

    @plugin
    def hostname(fqdn: "string") -> "string":
        """
            Return the hostname part of the fqdn
        """
        return fqdn.split(".")[0]
```


A test case, to test this plugin looks like this:

```python class: {.line-numbers}
    # <module-name>/tests/test_hostname.py

    def test_hostname(project):
        host = "test"
        fqdn = f"{host}.something.com"
        assert project.get_plugin_function("hostname")(fqdn) == host
```


* **Line 3:** Creates a pytest test case, which requires the `project` fixture.
* **Line 6:** Calls the function `project.get_plugin_function(plugin_name: str): FunctionType`, which returns the plugin
  function named `plugin_name`. As such, this line tests whether `host` is returned when the plugin function
  `hostname` is called with the parameter `fqdn`.

## Options

The following options are available.

 * --venv: folder in which to place the virtual env for tests (will be shared by all tests), overrides INMANTA_TEST_ENV.
   This options depends on symlink support. This does not work on all windows versions. On windows 10 you need to run pytest in an
   admin shell.
 * --module_repo: location to download modules from, overrides INMANTA_MODULE_REPO. The default value is the inmanta github organisation.
 
 Use the generic pytest options `--log-cli-level` to show Inmanta logger to see any setup or cleanup warnings. For example,
 `--log-cli-level=INFO`
