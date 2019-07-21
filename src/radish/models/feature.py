"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.models.timed import Timed
from radish.models.context import Context
from radish.models.state import State


class Feature(Timed):
    """"Represents a single instance of a Gherkin Feature"""

    def __init__(
        self,
        feature_id: int,
        short_description: str,
        description,
        tags,
        path: str,
        line: int,
        background,
        rules,
    ) -> None:
        self.id = feature_id
        self.short_description = short_description
        self.description = description
        self.tags = tags
        self.path = path
        self.line = line
        self.background = background
        self.rules = rules

        #: Holds the ``Context`` object.
        self.context = Context()

    def __repr__(self) -> str:
        return "<Feature: {id} '{short_description}' with {rules} Rules @ {path}:{line}>".format(
            id=self.id,
            short_description=self.short_description,
            rules=len(self.rules),
            path=self.path,
            line=self.line,
        )

    @property
    def state(self):
        """Read-only property to get the State for this Feature"""
        for rule_state in (r.state for r in self.rules):
            # TODO(TF): has feature to run?!
            if rule_state is not State.PASSED:
                return rule_state

        return State.PASSED

    # def has_to_run(self, tag_expression):
        # """Evaluate if this Feature has to run or not

        # The Scenario needs to be run if any of the following conditions is True:
        # * No ``tag_expression`` is given
        # * The ``tag_expression`` evaluates to True on the Scenario Tags
        # * The ``tag_expression`` evaluates to True on the Feature Tags
        # * No ``scenario_ids`` is given
        # * The ``scenario_ids`` is given and contains this Scenarios Id
        # """
        # has_to_run_tag_expression = True
        # has_to_run_scenario_ids = True

        # if tag_expression:
            # tag_names = [t.name for t in self.tags + self.feature.tags]
            # has_to_run_tag_expression = tag_expression.evaluate(tag_names)

        # if scenario_ids:
            # has_to_run_scenario_ids = self.id in scenario_ids

        # if tag_expression and scenario_ids:
            # return has_to_run_tag_expression and has_to_run_scenario_ids
        # elif tag_expression:
            # return has_to_run_tag_expression
        # elif scenario_ids:
            # return has_to_run_scenario_ids
        # else:
            # return True
