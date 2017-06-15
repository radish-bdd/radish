# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

*Stay tuned...*

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

[Unreleased]: https://github.com/radish-bdd/radish/compare/v0.6.3...HEAD
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
