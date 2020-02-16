"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import copy

from radish.models.constant_tag import ConstantTag
from radish.models.context import Context
from radish.models.state import State
from radish.models.timed import Timed


class Scenario(Timed):
    """Represents a single instance of a Gherkin Scenario"""

    def __init__(
        self,
        scenario_id: int,
        keyword: str,
        short_description: str,
        tags,
        path: str,
        line: int,
        steps,
    ) -> None:
        super().__init__()
        self.id = scenario_id
        self.keyword = keyword
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
        self.preconditions = None

        #: Holds the ``Context`` object.
        self.context = Context()

    def __repr__(self) -> str:
        return "<Scenario: {id} '{short_description} with {steps} Steps @ {path}:{line}>".format(
            id=self.id,
            short_description=self.short_description,
            steps=len(self.steps),
            path=self.path,
            line=self.line,
        )  # pragma: no cover

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return (
            self.short_description == other.short_description
            and self.path == other.path
            and self.line == other.line
        )

    def __hash__(self):
        return hash((self.short_description, self.path, self.line))

    def set_feature(self, feature):
        """Set the Feature for this Scenario"""
        self.feature = feature
        for step in self.steps:
            step.set_feature(feature)

    def set_background(self, background):
        """Set the Background for this Scenario"""
        if background:
            self.background = copy.deepcopy(background)
            self.background.set_scenario(self)
            self.background.set_rule(self.rule)
            self.background.set_feature(self.feature)

    def set_rule(self, rule):
        """Set the Rule for this Scenario"""
        self.rule = rule
        for step in self.steps:
            step.set_rule(rule)
        if self.preconditions:
            for precondition in self.preconditions:
                precondition.set_rule(rule)

    def set_preconditions(self, preconditions):
        """Set Preconditions for this Scenario"""
        if preconditions:
            self.preconditions = copy.deepcopy(preconditions)
            for precondition in self.preconditions:
                for step in precondition.steps:
                    step.set_scenario(self)

    def _steps_state(self, steps):
        """Get the State for some Steps"""
        return State.report_state(s.state for s in steps)

    @property
    def state(self):
        """Get the State of this Scenario"""
        steps = self.steps
        if self.background:
            state = self.background.state
            if state is State.FAILED:
                return state
            steps = self.steps + self.background.steps

        return self._steps_state(steps)

    @property
    def constants(self):
        """Get the Constants of this Scenario

        The Constants are lazy-evaluated from the Tags.
        """
        consts = self.feature.constants
        consts.update({t.key: t.value for t in self.tags if isinstance(t, ConstantTag)})
        return consts

    def get_all_tags(self):
        """Return all Tags for this Scenario

        These Tags include the ones inherited from the Feature, too.
        Use `Scenario.tags` to get only the tags declared for this Scenario.
        """
        return self.tags + self.feature.tags

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
            tag_names = [t.name for t in self.get_all_tags()]
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
