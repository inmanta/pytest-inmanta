# pytest-inmanta

A pytest plugin to test inmanta modules

## Installation

```bash
pip install pytest-inmanta
```

If you want to use `pytest-inmanta` to test a v2 module, make sure to install the module:
```bash
inmanta module install -e .
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

And allows deployment of specific resources

```python
    # perform deploy
    result = project.deploy_resource_v2("std::ConfigFile", expected_status=inmanta.const.ResourceState.deployed)
    # assert the deploy performed no changes
    result.assert_no_changes()
    # assert the deploy produced specific log lines
    result.assert_has_logline("Calling read_resource")
```

And dryrun

```python
    result = project.dryrun_resource_v2("testmodule::Resource")
    assert result.changes == {"value": {'current': 'read', 'desired': 'write'}}
    # Or dryrun all resources at once
    result = project.dryrun_all()
```

It is also possible to deploy all resources at once:

```python
    results = project.deploy_all()
    assert results.get_context_for("std::ConfigFile", path="/tmp/test").status == ResourceState.deployed
```
The `dryrun_all` and `deploy_all` functions return a `Result` object with
some helpful auxiliary functions to assert some sanity checks.

We can check if every resource on the result has the correct state:
```python
    results = project.dryrun_all()
    results.assert_all(ResourceState.dry)
```

It is possible to determine if every resource has the attribute `purged` in its changes.
This is helpful to assert if the resources are to be created (`purged` set to True) or deleted (`purged` set to False):
```python
    results = project.dryrun_all()
    results.assert_resources_have_purged()
```

The same applies to a `deploy_all`:
```python
    results = project.deploy_all()
    results.assert_all(ResourceState.deployed)
```

To check if a deploy is successful and we achieved the desired state,
it is possible to do a dryrun after the deploy and check if there are no changes:

```python
    results = project.deploy_all()
    results.assert_all(ResourceState.deployed)

    results = project.dryrun_all()
    results.assert_has_no_changes()
```

For convenience, it is also possible to dryrun and deploy all resources at once.
This method also asserts that the dryruns and deploys pass the sanity checks above.
It returns a `DeployResultCollection` that aggregates the `Results` from the dryruns and the deploy.

```python
    resutls = project.dryrun_and_deploy_all(assert_create_or_delete=True)
    results.first_dryrun.assert_all(ResourceState.dry)
    results.deploy.assert_all(ResourceState.deployed)
    results.last_dryrun.assert_all(ResourceState.dry)
```


Testing functions and classes defined in a v1 module is also possible
using the `inmanta_plugins` fixture. The fixture exposes inmanta modules as its attributes
and imports them dynamically when accessed. For v2 modules, the recommended approach is to
just use top-level imports instead of using the fixture.

```python
    def test_example(inmanta_plugins):
        inmanta_plugins.testmodule.regular_function("example")
```

This dynamism is required because the compiler resets module imports when `project.compile`
is called. As a result, if you store a module in a local variable, it will not survive a
compilation. Therefore you are advised to access modules in the `inmanta_plugins` package
in a fully qualified manner (using the fixture). The following example demonstrates this.

```python
    def test_module_inequality(project, inmanta_plugins):
        cached_module = inmanta_plugins.testmodule
        assert cached_module is inmanta_plugins.testmodule

        project.compile("import testmodule")

        assert cached_module is not inmanta_plugins.testmodule
```

While you could import from the `inmanta_plugins` package directly, the fixture makes abstraction
of module reloading. Without the fixture you would be required to reimport after `project.compile`.

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

## Advanced usage

Because pytest-inmanta keeps `inmanta_plugins` submodule objects alive to support top-level imports, any stateful modules
(modules that keep state on global Python variables in the module's namespace) must define cleanup logic to reset state between
compiles. Pytest-inmanta expects such cleanup functions to be synchronous functions that live in the top-level scope (defined
on the module object, not in a class) of a `inmanta_plugins` submodule (of any depth). Their name should start with
"inmanta\_reset\_state" and they should not take any parameters. For example:

```python
    # <module-name>/plugins/state.py

    MY_STATE = set()

    def inmanta_reset_state() -> None:
        global MY_STATE
        MY_STATE = set()
```

Multiple cleanup functions may be defined, in which case no guaranteed call order is defined.

## Options

The following options are available.

 * `--venv`: folder in which to place the virtual env for tests (will be shared by all tests), overrides `INMANTA_TEST_ENV`.
   This options depends on symlink support. This does not work on all windows versions. On windows 10 you need to run pytest in an
   admin shell. Using a fixed virtual environment can speed up running the tests.
 * `--pip-index-url`: pip index to install dependencies from. Can be specified multiple times to add multiple indexes. When set, it will overwrite the system index-url even if `pip-use-system-config` is set. (overrides `PIP_INDEX_URL`, defaults to `[]`)
 * `--pip-pre`, `--no-pip-pre` Allow installation of pre-release package by pip or not? (overrides `PIP_PRE`, defaults to  `--install-mode != release` )
 * `--pip-use-system-config` Allow pytest-inmanta to use the system pip config or not? (overrides `INMANTA_PIP_USE_SYSTEM_CONFIG`, defaults to `False`)
 * `--use-module-in-place`: makes inmanta add the parent directory of your module directory to it's directory path, instead of copying your
    module to a temporary libs directory. It allows testing the current module against specific versions of dependent modules. 
    Using this option can speed up the tests, because the module dependencies are not downloaded multiple times.
 * `--module-repo`: location to download v1 modules from, overrides `INMANTA_MODULE_REPO`. The default value is the inmanta github organisation.
    Multiple repos can be passed by space-separating them or by passing the parameter multiple times.
 * `--install-mode`: install mode to use for v1 modules downloaded during this test, overrides `INMANTA_INSTALL_MODE`.
 * `--no-load-plugins`: Don't load plugins in the Project class. Overrides `INMANTA_NO_LOAD_PLUGINS`. 
 When not using this option during the testing of plugins with the `project.get_plugin_function` method, 
 it's possible that the module's `plugin/__init__.py` is loaded multiple times, 
 which can cause issues when it has side effects, as they are executed multiple times as well.
 * `--no-strict-deps-check`: option to run pytest-inmanta using the legacy check(less strict) on requirements. By default the new strict will be used.
 
 Use the generic pytest options `--log-cli-level` to show Inmanta logger to see any setup or cleanup warnings. For example,
 `--log-cli-level=INFO`

## Compatibility with pytest-cov

The `--use-module-in-place` option should be set when pytest-inmanta is used in combination with the `pytest-cov` pytest plugin. Without the `--use-module-in-place` option, the reported test coverage will be incorrect.

## Using the pytest option framework

The `pytest-inmanta` extension contains a framework to help create pytest options to use in your test suite or test extension.  Options/parameters created with the framework will automatically be registered and picked up by pytest.  

Each option can be set via cli argument or via environment variable.  If both are set, the cli argument value takes precedence over the environment variable.  

When creating a new option, pay attention to place it in a place that will always be loaded by pytest, e.g. the `conftest.py` file.

The different type of test parameters that can be used are shown here: [`pytest_inmanta/test_parameters`](pytest_inmanta/test_parameter).  The currently supported types are:
 - [`BooleanTestParameter`](pytest_inmanta/test_parameter/boolean_parameter.py)
 - [`EnumTestParameter`](pytest_inmanta/test_parameter/enum_parameter.py)
 - [`FloatTestParameter`](pytest_inmanta/test_parameter/float_parameter.py)
 - [`IntegerTestParameter`](pytest_inmanta/test_parameter/integer_parameter.py)
 - [`ListTestParameter`](pytest_inmanta/test_parameter/list_parameter.py)
 - [`PathTestParameter`](pytest_inmanta/test_parameter/path_parameter.py)
 - [`StringTestParameter`](pytest_inmanta/test_parameter/string_parameter.py)  

You can of course add and use your own option type, as long as it extends the base class [`TestParameter`](pytest_inmanta/test_parameter/parameter.py) properly.
