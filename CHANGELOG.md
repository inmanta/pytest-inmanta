# Changelog

## v4.1.0 - 2026-11-09

- Dropped the pkg_resources package.
- Use the vendored version of the pip2pi package in core when available.
- Fix compatibility with pytest 9.2.

## v4.0.0 - 2025-11-18

- No longer install dependencies for test projects. Modules used in testing should now be added as dev dependencies, like any other package required during testing.
- Add support for skip in reference
- Fix memory leak caused by pytest LogCaptureHandler.  Address it by clearing the old in-memory logs before each compile.
- Fix incompatibility with versions of inmanta-core that have support to push environment settings to the server.
- Reset the compiler state between two consecutive compiles
- Fix potential import loop when using test parameters

## v3.2.0 - 2025-04-09

- Add support for references
- Format code using black 25.1.0
- Make sure to use pydantic v2+ methods
- Fix configuration of temporary state dir with the project fixture
- Remove reference to deprecated module install command

## v3.1.0 - 2024-10-10

- Allow to use relative path for PathTestParameter
- Add compatibility with ISO8 AgentCache

## v3.0.0 - 2024-08-19

- Remove io support to be compatible with ISO8
- Add strict mode in `get_resource` method to  the `project` fixture and `Result` object (by default set to `False`). 

### Updating
- All uses of the `get_resource` method should be replaced with the `get_one_resource` method. It has improved type matching and raises an exception when multiple matches are present.

## v2.10.0 - 2024-07-05

- Add support for custom `agent_map` enabling testing or remote io scenarios.
- Fix resource serialization (#437)
- Fix new agent api in inmanta.agent.executor.AgentInstance (ISO8)
- Add `get_one_resource` method to the `project` fixture and `Result` object.

## v2.9.0 - 2023-11-29

- Add support for more values (yes, 1) and (no, 0) for boolean options
- Add `deploy_resouce_v2` endpoint
- Add support for unmanaged resources
- Adds a new resource entity that raises an IgnoreResourceException when buildings its id
- Add support for ISO7. 
- Add `--pip-pre`, `--pip-use-system-config` and `--pip-index-url`

## v2.8.0 - 2023-08-03

- Log a warning when the id_attribute of a resource is called id.
- Ignore `__pycache__` dirs when copying the current module to the test project dir
- Introduce `--pip-index-url` option to set corresponding project config section for inmanta-core 9.0.
- Dropped nonexistent option from the README

## v2.7.0 - 2023-02-23

- Introduce `project_metadata` fixture to allow modifying the `project.yml` file for the project created by the project fixture.

## v2.6.0 - 2023-02-02

- Add `dryrun_all` method to  the `project` fixture. Does a dryrun on every resource of a project. Also does some sanity checks.
- Add `dryrun_and_deploy_all` method to the `project` fixture. Dryruns, deploys and does a final dryrun on every resource of a project. Also does some sanity checks.
## v2.5.0 - 2023-01-20

- Fix bug where the temporary directory used to store the Inmanta project is not cleaned up when an exception occurs in the setup stage of the project\_factory fixture.

## v2.4.0 - 2022-09-07

- Add fixture to change the Inmanta state dir to a writable location for the current user.
- Add a new '--no-strict-deps-check' option to run pytest-inmanta using the legacy check on requirements.
By default the new strict check of core will be used.

## v2.3.3 - 2022-05-18

 - Fix enum test parameters registered after pytest has loaded pytest-inmanta plugin.

## v2.3.2 - 2022-05-17

 - Allow other plugins to register test parameters after pytest has loaded pytest-inmanta plugin.

## v2.3.1 - 2022-05-16

 - Fixed test parameter framework for boolean options.

## v2.3.0 - 2022-05-13

- Added test parameter framework (#288).
- Some options have been deprecated:
  -  `--no_load_plugins` in favor of `--no-load-plugins` (and `INMANTA_TEST_NO_LOAD_PLUGINS` in favor of `INMANTA_NO_LOAD_PLUGINS`)
  -  `--module_repo` in favor of `--module-repo`
  -  `--install_mode` in favor of `--install-mode`

## v2.2.0 - 2022-04-26

- The `project` fixture now makes `sys.executable` point to the compiler's executable

## v2.1.0 - 2022-03-30

- Fix bug where the `project` fixture doesn't reset the current working directory in the cleanup stage.
- Add deploy_all method to the `project` fixture

## v2.0.0 - 2022-01-24

- Added support for testing v2 modules.
- Extended to be compatible with `inmanta-core>=6`
- Added support for custom `inmanta_reset_state` method to clean up stateful modules between compiles
- Ensure that projects are compiled using a separate venv.
- Fixed typing issue for `filter_args` in different method of the Project class.

### Breaking changes
- pytest-inmanta now keeps `inmanta_plugins` submodules alive across compiles. As a result, stateful modules must implement
    custom state cleanup logic as described in the README.

## v1.6.2 - 2021-08-17

- Fixed issue with project fixture related to cleanup assumptions causing failures for `inmanta-core>=5.1.2.dev`

## v1.6.1 - 2021-06-29

- Fixed an invalid import from inmanta-core (inmanta/inmanta-core#3074)

## v1.6.0 - 2021-06-18

- Added the ability to assert the expected 'change' of a deploy
- Compiled models are logged (debug level), with line numbers (#199)
- Export mypy types

## v1.5.0 - 2021-03-26

- Remove dependency on the inmanta package

# V 1.4.0 (20-10-12)

- Added meaningful error message when --venv points to a non-existing directory (#62)
- Ensure that cache is closed completely (#57)
- Fix incompatibility with pytest 6.0.0
- Fixed plugin loading compatibility with compiler's import mechanism (#46, #49)
- Added `inmanta_plugins` fixture to make abstraction of required module reloading when the compiler project is reset (related to #49)
- Added deprecation warning for `project_no_plugins` fixture in favor of `INMANTA_TEST_NO_LOAD_PLUGINS` environment variable (#66)
- Added resource unittest::IgnoreResource.
- Improve documentation of options (#67)

# V 1.3.0

- Added INMANTA_TEST_NO_LOAD_PLUGINS environment variable as workaround for inmanta/pytest-inmanta#49

# V 1.2.0

- Fixed status field on dryrun_resource (#53)
- Fixed error when running tests for module that imports other modules from its plugins
- Added project_no_plugins fixture as workaround for plugins being loaded multiple times (inmanta/pytest-inmanta#49)

# V 1.1.0

- Added --use-module-in-place option (#30)
- Added support to test regular functions and classes (#37)
- Close handler caches on cleanup (#42)

# V 1.0.0

- Added support to get logs from handler (#35)
- Added support to specify multiple --repo-path options (#38)
- Added --install_mode option

# V 0.10.0


# V 0.9.0


### Added
- Added support to retrieve scopes in project fixture.
- Test the serialization/deserialization of resources.

## Fixed
- Ensure that the project fixture doesn't leak any data across test cases.

# V 0.8.0

- Add suport for skip and fail through data global

# V 0.7.2

- Prevent IOError when using remote IO

# V 0.7.1

- Fix packaging bug

# V 0.7.0

- Various bugfixes
- Use yaml.safe_load() instead of yaml.load()
- Documentation on how to test plugins
- Add unittest handlers

# V 0.6.0

- added log serialization to deploy, to better mimic agent behavior
- added dryrun
