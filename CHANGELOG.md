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
