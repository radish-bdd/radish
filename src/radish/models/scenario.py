"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.models.timed import Timed


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
        self.background = background

    def set_rule(self, rule):
        """Set the Rule for this Scenario"""
        self.rule = rule
        for step in self.steps:
            step.set_rule(rule)