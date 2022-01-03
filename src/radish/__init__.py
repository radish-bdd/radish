"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

try:
    from importlib.metadata import version
except ImportError:
    # NOTE(TF): This is a workaround for the lack of importlib.metadata in Python < 3.8
    import pkg_resources
    __version__ = pkg_resources.get_distribution("radish-bdd").version
else:
    __version__ = version("radish-bdd")

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
