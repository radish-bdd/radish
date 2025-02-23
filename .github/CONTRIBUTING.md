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

radish can be installed as [editable install](https://setuptools.pypa.io/en/latest/userguide/development_mode.html).

```bash
pip install -r requirements-dev.txt
pip install -e .
```

### tox: linting, testing, docs & more

radish uses [`tox`](https://tox.readthedocs.io/en/latest/) to automate development tasks,
like linting, testing, building the docs and creating the changelog.

The radish tox setup provides the following automated tasks:

* `lint`: formats and lints the code base using [`black`](https://black.readthedocs.io/en/stable/) and [`flake8`](https://flake8.readthedocs.io/en/stable/).
* `py<ver>`: runs tests with the Python Version from `<ver>`.

Before commiting your changes, it's a good practice to run `tox`.
So that it'll run all the preconfigured tasks.
If they all pass - you are good to go for a Pull Request! :tada:
