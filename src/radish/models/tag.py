"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class Tag:
    """Represents a single Gherkin Tag"""

    def __init__(self, name: str, path: str, line: int) -> None:
        self.name = name
        self.path = path
        self.line = line

    def __repr__(self) -> str:
        return "<Tag: {name} @ {path}:{line}>".format(
            name=self.name, path=self.path, line=self.line
        )  # pragma: no cover
