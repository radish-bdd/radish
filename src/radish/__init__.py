"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

__description__ = "Behaviour-Driven-Development tool for python"
__license__ = "MIT"
__version__ = "1.0.0a5"
__author__ = "Timo Furrer"
__author_email__ = "tuxtimo@gmail.com"
__url__ = "http://radish-bdd.io"
__download_url__ = "https://github.com/radish-bdd/radish"
__bugtrack_url__ = "https://github.com/radish-bdd/radish/issues"


# Expose useful objects on radish package level
from radish.errors import RadishError  # noqa
from radish.hookregistry import (  # noqa
    after,
    before,
    each_feature,
    each_rule,
    each_scenario,
    each_step,
    for_all,
)
from radish.models import (  # noqa
    Background,
    ConstantTag,
    DefaultRule,
    Feature,
    PreconditionTag,
    Rule,
    Scenario,
    ScenarioLoop,
    ScenarioOutline,
    Step,
    Tag,
)
from radish.parser import FeatureFileParser  # noqa
from radish.parsetyperegistry import (  # noqa
    TypeBuilder,
    custom_type,
    register_custom_type,
)
from radish.stepregistry import given, step, then, when  # noqa
from radish.terrain import world  # noqa
