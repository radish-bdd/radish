# Contributing

Thank you for helping radish to get a better and better! :tada:

## Support

If you have any questions regarding the usage of radish please use
[a GitHub Issue](https://github.com/radish-bdd/radish/issues/new?assignees=&labels=question&template=question.md&title=).

## Reporting Bugs / Proposing Features

Before you submit a Bug or propose a Feature check the existing Issues in order to avoid duplicates. <br>
Please make sure you provide enough information to work on your submitted Bug or proposed Feature:

* Which version of radish are you using?
* Which version of Python are you using?
* On which platform are you running radish?

Make sure to use the GitHub Template when reporting an Issue.

It's best if you can provide a small-ish standalone example of the Bug you discovered
or the Feature you have in mind.

## Pull Requests

We are very happy to receive Pull Requests considering:

* Style Guide. Follow the rules of [PEP8](http://legacy.python.org/dev/peps/pep-0008/) and make sure `tox -e lint` passes on your changes.
* Tests. Make sure your code is covered by an automated test case. Make sure all tests pass.

## Development

radish uses the *extra* requirements feature of `setuptools` to specify all
the dependencies needed to develop radish.
A set of extra requirements can be installed with the following `pip` syntax:

```bash
pip install -e '.[<extras>]'
```

whereas `<extras>` can be one of:

* `tests`: all dependencies required to run the radish unit and integration tests
* `docs`: all dependencies required to build the radish documentation
* `dev`: all dependencies required to develop radish. This group includes the `tests` and `docs` dependencies. [recommended]

### tox: linting, testing, docs & more

radish uses [`tox`](https://tox.readthedocs.io/en/latest/) to automate development tasks,
like linting, testing, building the docs and creating the changelog.

The radish tox setup provides the following automated tasks:

* `lint`: formats and lints the code base using [`black`](https://black.readthedocs.io/en/stable/) and [`flake8`](https://flake8.readthedocs.io/en/stable/).
* `manifest`: checks if the `MANIFEST.in` content is consistent with the repository content.
* `py<ver>`: runs unit tests with the Python Version from `<ver>`.
* `integration`: runs integration tests.
* `coverage-report`: generates a coverage report. Make sure that you've run some tests before.
* `docs`: builds the sphinx documentation.
* `news`: generates the ChangeLog from the newsfragments in `changelog/`. Use `towncrier --draft` directly to generate a ChangeLog draft.

Before commiting your changes, it's a good practice to run `tox`.
So that it'll run all the preconfigured tasks.
If they all pass - you are good to go for a Pull Request! :tada:
