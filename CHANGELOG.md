# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

*Stay tuned...*

## [v0.14.0]
### Changes

- Drop Python 2.7 and Python 3.4
- Switched to colorful 0.5.4 (slightly different output rendering)
- Switch and fix CI to run on GitHub Actions
- Test support for new Python versions 3.9, 3.10
- Fix warnings unknown escape strings, wrong comparison
- Use latests dependencies available on Python3.5

## [v0.13.4]
### Fixed

- Parse -s/--scenarios with = sign correctly
- Fix radish matcher print
- Update Background example in docs

## [v0.13.3]
### Fixed

- Fix duration in cucumber JSON report

## [v0.13.2]
### Fixed

- PEP 352 removed the 'message' attribute from Exceptions

## [v0.13.1]
### Fixed

- Support the PIPE (|) character in table cell values and Scenario Outline Examples

## [v0.13.0]
### Added

- Support unicode characters in matcher tests due to new pyyaml

## [v0.12.1]
### Fixed

- Dedent lines for step text to be complient with gherkin parser

## [v0.12.0]
### Added

- Support multiple base paths on Windows.

## [v0.11.1]
### Fixed

- Markdown project description on pypi.org.

## [v0.11.0]
### Added

- Support for Hook ordering. See https://radish.readthedocs.io/en/latest/tutorial.html#ordered-hooks
- Support for unicode in Python 2 and Python 3

### Fixed

- Wrong duration issue due to changed timezones during a test run. Refs #188

## [v0.10.0]

- Implement `step.skip()` API to skip certain steps

## [v0.9.2]

- Fix unicode issues with the syslog writer extension

## [v0.9.1]

- Fix error which was introduced with black formatting

## [v0.9.0]

- Implemented `--wip` feature.
- Implemented basics for formatters
- Implemented `gherkin` and `dots` formatters.

## [v0.8.6]

- Fix markdown for PyPI

## [v0.8.5]

- Fix markdown for PyPI

## [v0.8.4]

- Use markdown for setuptools long description

## [v0.8.3]
### Added
- Implement `use_repr` flag to use repr protocol for argument value testing

## [v0.8.2]
### Fixed
- Copy extended step data for outlined and iteration steps. Refs #208

## [v0.8.1]
### Fixed
- Support parsing unnamed Backgrounds
- Add exception-handling for dictionary

## [v0.8.0]
### Fixed
-  Require header in step table. Refs #185

## [v0.7.3]
### Fixed
- Do not import alternative parse class

## [v0.7.2]
### Added
- Support bad-case testing for step patterns

## [v0.7.1]
### Fixed
- Allow leading and trailing colon for basepath

## [v0.7.0]
### Added
- Split multiple basepaths with a colon (:)

## [v0.6.8]
### Refactored
- Entire test suite is using pytest

### Fixed
- Typo in matches

## [v0.6.7]
### Fixed
- Correctly match "matching" sentences which do not match perfectly

## [v0.6.6]
### Fixed
- Beautify duration output. Refs #138

## [v0.6.5]
### Fixed
- Precondition with tags from other Scenario parsed correctly
- Fix printing of tags

## [v0.6.4]
### Added
- Support QuotedString custom type. Refs #134
- Support Boolean custom type. Refs #132

### Fixed
- Precondition Scenarios from same Feature. Fixes #136

## [v0.6.3]
### Fixed
- Remove `DeprecationWarning` when using Python 3.6. Refs #133

## [v0.6.2]
### Added
- Support specifying arbitrary user data per run. Refs #124, #127

## [v0.6.1]
### Fixed
- Fix syslog extension

## [v0.6.0]
### Added
- Support cardinalities in step patterns. Refs #62, #113
- Highlight placeholders in Scenario Outline. Refs #60, #122
- Correctly support step gherkin context (`Given`, `When`, `Then`) when using `And`. Refs #61
- Add french translation

### Changed
- Renamed *argument expressions* to *custom types*

### Fixed
- Fixed importing `importlib.util`. Refs #123

## [v0.5.1]
### Fixed
- Fix parsing Scenarios with tag and last in feature. Refs #111
- Fix background and precondition console writing

## [v0.5.0]

### Added
- Support tag specific hooks
- Support multiple basedirs for single run call. Refs #40

### Fixed
- Parsing of tagged Scenario after Scenario Outline Example Table. Refs #105

## [v0.4.1]
### Added
- Use new colorful
- Galician language
- Declare extension dependencies as extra requirements. Refs #73

### Fixed
- Traceback when `--early-exit` was set and a run failed. Refs #92


## [v0.4.0]
### Added
- Support for Background. Refs #57
- **API break**, Merged `--feature-tags` and `--scenario-tags` to `--tags` command line option. Refs #72
- Pinned colorful version to 0.1.3 until new colorful version is out.

## [v0.3.2]

### Changed
- Disabled the *syslog extension* by default. It can be enabled via the `--syslog` command line option. Refs #49

## [v0.3.1]

### Fixed
- Remove vendored `parse` package because [parse (#38)](https://github.com/r1chardj0n3s/parse/pull/38) is merged

## [v0.3.0]

### Added
- Vendor `parse` package until [parse (#38)](https://github.com/r1chardj0n3s/parse/pull/38) is merged
- Implement `radish-test` to test step patterns
- Improved coverage extensions with useful CLI options. Refs #15 and #41
- Support for [tag-expressions](https://github.com/timofurrer/tag-expressions) for `--feature-tags` and `--scenario-tags`. Refs #16

### Fixed
- Lazy evaluate matched step arguments. Refs #31
- Support running features containing steps with missing step definitions if they are ignored by tags. Refs #17

## [v0.2.12]
### Added
- Python 3.6 support
- Python 3.7-dev support (allowed to fail)


## No previous changelog history.

Please see `git log`

[Unreleased]: https://github.com/radish-bdd/radish/compare/v0.14.0...HEAD
[v0.14.0]: https://github.com/radish-bdd/radish/compare/v0.13.4...v0.14.0
[v0.13.4]: https://github.com/radish-bdd/radish/compare/v0.13.3...v0.13.4
[v0.13.3]: https://github.com/radish-bdd/radish/compare/v0.13.2...v0.13.3
[v0.13.2]: https://github.com/radish-bdd/radish/compare/v0.13.1...v0.13.2
[v0.13.1]: https://github.com/radish-bdd/radish/compare/v0.13.0...v0.13.1
[v0.13.0]: https://github.com/radish-bdd/radish/compare/v0.12.1...v0.13.0
[v0.12.1]: https://github.com/radish-bdd/radish/compare/v0.12.0...v0.12.1
[v0.12.0]: https://github.com/radish-bdd/radish/compare/v0.11.1...v0.12.0
[v0.11.1]: https://github.com/radish-bdd/radish/compare/v0.11.0...v0.11.1
[v0.11.0]: https://github.com/radish-bdd/radish/compare/v0.10.0...v0.11.0
[v0.10.0]: https://github.com/radish-bdd/radish/compare/v0.9.2...v0.10.0
[v0.9.2]: https://github.com/radish-bdd/radish/compare/v0.9.1...v0.9.2
[v0.9.1]: https://github.com/radish-bdd/radish/compare/v0.9.0...v0.9.1
[v0.9.0]: https://github.com/radish-bdd/radish/compare/v0.8.6...v0.9.0
[v0.8.6]: https://github.com/radish-bdd/radish/compare/v0.8.5...v0.8.6
[v0.8.5]: https://github.com/radish-bdd/radish/compare/v0.8.4...v0.8.5
[v0.8.4]: https://github.com/radish-bdd/radish/compare/v0.8.3...v0.8.4
[v0.8.3]: https://github.com/radish-bdd/radish/compare/v0.8.2...v0.8.3
[v0.8.2]: https://github.com/radish-bdd/radish/compare/v0.8.1...v0.8.2
[v0.8.1]: https://github.com/radish-bdd/radish/compare/v0.8.0...v0.8.1
[v0.8.0]: https://github.com/radish-bdd/radish/compare/v0.7.3...v0.8.0
[v0.7.3]: https://github.com/radish-bdd/radish/compare/v0.7.2...v0.7.3
[v0.7.2]: https://github.com/radish-bdd/radish/compare/v0.7.1...v0.7.2
[v0.7.1]: https://github.com/radish-bdd/radish/compare/v0.7.0...v0.7.1
[v0.7.0]: https://github.com/radish-bdd/radish/compare/v0.6.8...v0.7.0
[v0.6.8]: https://github.com/radish-bdd/radish/compare/v0.6.7...v0.6.8
[v0.6.7]: https://github.com/radish-bdd/radish/compare/v0.6.6...v0.6.7
[v0.6.5]: https://github.com/radish-bdd/radish/compare/v0.6.4...v0.6.5
[v0.6.4]: https://github.com/radish-bdd/radish/compare/v0.6.3...v0.6.4
[v0.6.3]: https://github.com/radish-bdd/radish/compare/v0.6.2...v0.6.3
[v0.6.2]: https://github.com/radish-bdd/radish/compare/v0.6.1...v0.6.2
[v0.6.1]: https://github.com/radish-bdd/radish/compare/v0.6.0...v0.6.1
[v0.6.0]: https://github.com/radish-bdd/radish/compare/v0.5.1...v0.6.0
[v0.5.1]: https://github.com/radish-bdd/radish/compare/v0.5.0...v0.5.1
[v0.5.0]: https://github.com/radish-bdd/radish/compare/v0.4.1...v0.5.0
[v0.4.1]: https://github.com/radish-bdd/radish/compare/v0.4.0...v0.4.1
[v0.4.0]: https://github.com/radish-bdd/radish/compare/v0.3.2...v0.4.0
[v0.3.2]: https://github.com/radish-bdd/radish/compare/v0.3.1...v0.3.2
[v0.3.1]: https://github.com/radish-bdd/radish/compare/v0.3.0...v0.3.1
[v0.3.0]: https://github.com/radish-bdd/radish/compare/v0.2.12...v0.3.0
[v0.2.12]: https://github.com/radish-bdd/radish/compare/v0.2.11...v0.2.12
