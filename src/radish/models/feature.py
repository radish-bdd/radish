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
        super().__init__()
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
            if rule_state is not State.PASSED:
                return rule_state

        return State.PASSED

    def has_to_run(self, tag_expression, scenario_ids):
        """Evaluate if this Feature has to run or not

        A Feature has to run of any of it's Rules has to be run.
        """
        return any(r.has_to_run(tag_expression, scenario_ids) for r in self.rules)
