"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class Scenario:
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
        self.background = None

    def __repr__(self) -> str:
        return "<Scenario: {id} '{short_description} with {steps} Steps @ {path}:{line}>".format(
            id=self.id,
            short_description=self.short_description,
            steps=len(self.steps),
            path=self.path,
            line=self.line,
        )

    def set_background(self, background):
        """Set the Background for this Scenario"""
        self.background = background
