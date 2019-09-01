"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.models.tag import Tag


class PreconditionTag(Tag):
    """Represents a single radish Precondition Tag"""

    def __init__(
        self,
        feature_filename: str,
        scenario_short_description: str,
        path: str,
        line: int,
    ) -> None:
        super().__init__(
            "precondition({}: {})".format(feature_filename, scenario_short_description),
            path,
            line,
        )
        self.feature_filename = feature_filename
        self.scenario_short_description = scenario_short_description

    def __repr__(self) -> str:
        return "<PreconditionTag: {name} @ {path}:{line}>".format(
            name=self.name, path=self.path, line=self.line
        )  # pragma: no cover
