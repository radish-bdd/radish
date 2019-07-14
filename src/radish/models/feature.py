"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class Feature:
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

    def __repr__(self) -> str:
        return "<Feature: {id} '{short_description}' with {rules} Rules @ {path}:{line}>".format(
            id=self.id,
            short_description=self.short_description,
            rules=len(self.rules),
            path=self.path,
            line=self.line,
        )
