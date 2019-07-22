"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.models.scenario import Scenario
from radish.models.state import State


class Background(Scenario):
    """Represents a single instance of a Gherkin Background"""

    def __init__(self, short_description: str, path: str, line: int, steps) -> None:
        super().__init__(0, short_description, None, path, line, steps)

    def __repr__(self) -> str:
        return "<Background: '{short_description} with {steps} Steps @ {path}:{line}>".format(
            short_description=self.short_description,
            steps=len(self.steps),
            path=self.path,
            line=self.line,
        )

    @property
    def state(self):
        """Get the State of this Scenario"""
        for step in self.steps:
            if step.state is not State.PASSED:
                return step.state

        return State.PASSED
