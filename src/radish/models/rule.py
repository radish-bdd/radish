"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class Rule:
    """Represents a single instance of a Gherkin Rule"""

    def __init__(self, short_description, path: str, line: int, scenarios) -> None:
        self.short_description = short_description
        self.path = path
        self.line = line
        self.scenarios = scenarios

        self.feature = None

    def __repr__(self) -> str:
        return "<Rule: '{short_description}' with {scenarios} Scenarios @ {path}:{line}>".format(
            short_description=self.short_description,
            scenarios=len(self.scenarios),
            path=self.path,
            line=self.line,
        )

    def set_feature(self, feature):
        """Set the Feature for this Rule"""
        self.feature = feature
        for scenario in self.scenarios:
            scenario.set_feature(feature)

    def set_background(self, background):
        """Set the Background for all Scenarios in this Rule"""
        for scenario in self.scenarios:
            scenario.set_background(background)


class DefaultRule(Rule):
    """Represents the default Rule which is used if no rule is specified"""

    def __init__(self, path: str, line: int, scenarios) -> None:
        super().__init__(None, path, line, scenarios)

    def __repr__(self) -> str:
        return "<DefaultRule: with {scenarios} Scenarios @ {path}:{line}>".format(
            scenarios=len(self.scenarios), path=self.path, line=self.line
        )
