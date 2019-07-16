"""
radish
~~~~~~

the root from red to green.  BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""


class Step:
    """Respresents a single instance of a Gherkin Step"""

    def __init__(
        self,
        step_id: int,
        keyword: str,
        text: str,
        doc_string,
        data_table,
        path: str,
        line: int,
    ) -> None:
        self.id = step_id
        self.keyword = keyword
        self.text = text
        self.doc_string = doc_string
        self.data_table = data_table
        self.path = path
        self.line = line

        self.step_impl = None
        self.step_impl_match = None

    def __repr__(self) -> str:
        return "<Step: {id} '{keyword} {text}' @ {path}:{line}>".format(
            id=self.id,
            keyword=self.keyword,
            text=self.text,
            path=self.path,
            line=self.line,
        )

    def assign_implementation(self, step_impl, match):
        """Assign a matched Step Implementation to this Step"""
        self.step_impl = step_impl
        self.step_impl_match = match
