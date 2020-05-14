# V 1.2.0
Changes in this release:
- Fixed status field on dryrun_resource (#53)

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
