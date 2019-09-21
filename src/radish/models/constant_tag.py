"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.models.tag import Tag


class ConstantTag(Tag):
    """Represents a single radish Constant Tag"""

    def __init__(self, key: str, value: str, path: str, line: int) -> None:
        super().__init__("constant({}: {})".format(key, value), path, line)
        self.key = key
        self.value = value

    def __repr__(self) -> str:
        return "<Constant: {name} @ {path}:{line}>".format(
            name=self.name, path=self.path, line=self.line
        )  # pragma: no cover
