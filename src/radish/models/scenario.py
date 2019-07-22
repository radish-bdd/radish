"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import copy

from radish.models.timed import Timed
from radish.models.state import State


class Scenario(Timed):
    """Represents a single instance of a Gherkin Scenario"""

    def __init__(
        self,
        scenario_id: int,
        short_description: str,
        tags,
        path: str,
        line: int,
        steps,
    ) -> None:
        super().__init__()
        self.id = scenario_id
        self.short_description = short_description
        self.tags = tags
        self.path = path
        self.line = line
        self.steps = steps

        for step in self.steps:
            step.set_scenario(self)

        self.feature = None
        self.background = None
        self.rule = None

    def __repr__(self) -> str:
        return "<Scenario: {id} '{short_description} with {steps} Steps @ {path}:{line}>".format(
            id=self.id,
            short_description=self.short_description,
            steps=len(self.steps),
            path=self.path,
            line=self.line,
        )

    def set_feature(self, feature):
        """Set the Feature for this Scenario"""
        self.feature = feature
        for step in self.steps:
            step.set_feature(feature)

    def set_background(self, background):
        """Set the Background for this Scenario"""
        self.background = copy.deepcopy(background)

    def set_rule(self, rule):
        """Set the Rule for this Scenario"""
        self.rule = rule
        for step in self.steps:
            step.set_rule(rule)

    @property
    def state(self):
        """Get the State of this Scenario"""
        if self.background:
            state = self.background.state
            if state is not State.PASSED:
                return state

        for step_state in (s.state for s in self.steps):
            if step_state is not State.PASSED:
                return step_state

        return State.PASSED

    def has_to_run(self, tag_expression, scenario_ids):
        """Evaluate if this Scenario has to run or not

        The Scenario needs to be run if any of the following conditions is True:
        * No ``tag_expression`` is given
        * The ``tag_expression`` evaluates to True on the Scenario Tags
        * The ``tag_expression`` evaluates to True on the Feature Tags
        * No ``scenario_ids`` is given
        * The ``scenario_ids`` is given and contains this Scenarios Id
        """
        has_to_run_tag_expression = True
        has_to_run_scenario_ids = True

        if tag_expression:
            tag_names = [t.name for t in self.tags + self.feature.tags]
            has_to_run_tag_expression = tag_expression.evaluate(tag_names)

        if scenario_ids:
            has_to_run_scenario_ids = self.id in scenario_ids

        if tag_expression and scenario_ids:
            return has_to_run_tag_expression and has_to_run_scenario_ids
        elif tag_expression:
            return has_to_run_tag_expression
        elif scenario_ids:
            return has_to_run_scenario_ids
        else:
            return True
