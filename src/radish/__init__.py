"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

__description__ = "Behaviour-Driven-Development tool for python"
__license__ = "MIT"
__version__ = "1.0.0a1"
__author__ = "Timo Furrer"
__author_email__ = "tuxtimo@gmail.com"
__url__ = "http://radish-bdd.io"
__download_url__ = "https://github.com/radish-bdd/radish"
__bugtrack_url__ = "https://github.com/radish-bdd/radish/issues"


# Expose useful objects on radish package level
from radish.errors import RadishError  # noqa
from radish.hookregistry import after, before  # noqa
from radish.parsetyperegistry import custom_type  # noqa
from radish.stepregistry import given, step, then, when  # noqa
from radish.terrain import world  # noqa
