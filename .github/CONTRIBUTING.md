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

* Style Guide. Follow the rules of [PEP8](http://legacy.python.org/dev/peps/pep-0008/) and make sure `ruff format` and `ruff check --fix` passes on your changes.
* Tests. Make sure your code is covered by an automated test case. Make sure all tests pass.

## Development

Install the development dependencies with [uv](https://docs.astral.sh/uv/getting-started/installation/) this will create a virtual environment for you and install all dependencies there.
Make sure to install with `--all-extras` so that all optional dependencies are installed as well.

```bash
uv sync --all-extras
```

### Linting & Formatting

Radish uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting the code base.

```bash
uv run ruff check --fix
uv run format .
```

### Testing

To run the tests you can use pytest.

```bash
uv run pytest
```

If you want to run the tests for a specific Python version you can use `uv` to do so:

Make sure you have installed the development dependencies with that specific Python version first.

```bash
uv python install 3.10
```
Then you can run the tests like this (`--all-extras` since some tests require optional dependencies) (`--isolated` to avoid interference with the current environment):

```bash
uv run --isolated --python=3.11 --all-extras pytest
```
