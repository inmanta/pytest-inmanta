# V 1.4.0 (?)
Changes in this release:
- Added meaningful error message when --venv points to a non-existing directory (#62)
- Ensure that cache is closed completely (#57)
- Fix incompatibility with pytest 6.0.0
- Fixed plugin loading compatibility with compiler's import mechanism (#46, #49)
- Added `inmanta_plugins` fixture to make abstraction of required module reloading when the compiler project is reset (related to #49)
- Added deprecation warning for `project_no_plugins` fixture in favor of `INMANTA_TEST_NO_LOAD_PLUGINS` environment variable (#66)
- Added resource unittest::IgnoreResource.

# V 1.3.0
Changes in this release:
- Added INMANTA_TEST_NO_LOAD_PLUGINS environment variable as workaround for inmanta/pytest-inmanta#49

# V 1.2.0
Changes in this release:
- Fixed status field on dryrun_resource (#53)
- Fixed error when running tests for module that imports other modules from its plugins
- Added project_no_plugins fixture as workaround for plugins being loaded multiple times (inmanta/pytest-inmanta#49)

# V 1.1.0
Changes in this release:
- Added --use-module-in-place option (#30)
- Added support to test regular functions and classes (#37)
- Close handler caches on cleanup (#42)

# V 1.0.0
Changes in this release:
- Added support to get logs from handler (#35)
- Added support to specify multiple --repo-path options (#38)
- Added --install_mode option

# V 0.10.0
Changes in this release:

# V 0.9.0
Changes in this release:

## Added
- Added support to retrieve scopes in project fixture.
- Test the serialization/deserialization of resources.

## Fixed
- Ensure that the project fixture doesn't leak any data across test cases.

# V 0.8.0
Changes in this release:
- Add suport for skip and fail through data global

# V 0.7.2
Changes in this release:
- Prevent IOError when using remote IO

# V 0.7.1
Changes in this release:
- Fix packaging bug

# V 0.7.0
Changes in this release:
- Various bugfixes
- Use yaml.safe_load() instead of yaml.load()
- Documentation on how to test plugins
- Add unittest handlers

# V 0.6.0
Changes in this release:
- added log serialization to deploy, to better mimic agent behavior
- added dryrun 
