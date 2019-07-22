"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.errors import RadishError
from radish.models.state import State
from radish.models.timed import Timed
from radish.models.stepfailurereport import StepFailureReport


class Step(Timed):
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

        #: Holds information about the AST hierarchy where this Step appeared.
        self.feature = None
        self.rule = None
        self.scenario = None

        #: Holds information about the Step Implementation this Step was matched with.
        self.step_impl = None
        self.step_impl_match = None

        #: Holds information about the State of this Step
        self.state = State.UNTESTED
        self.failure_report = None

    def __repr__(self) -> str:
        return "<Step: {id} '{keyword} {text}' @ {path}:{line}>".format(
            id=self.id,
            keyword=self.keyword,
            text=self.text,
            path=self.path,
            line=self.line,
        )

    def set_feature(self, feature):
        """Set the Feature for this Step"""
        self.feature = feature

    def set_rule(self, rule):
        """Set the Rule for this Step"""
        self.rule = rule

    def set_scenario(self, scenario):
        """Set the Scenario for this Step"""
        self.scenario = scenario

    def assign_implementation(self, step_impl, match):
        """Assign a matched Step Implementation to this Step"""
        self.step_impl = step_impl
        self.step_impl_match = match

    def run(self):
        """Run this Step

        The Step will only run if a ``StepImpl`` was assigned using ``assign_implementation``.
        """
        if not self.step_impl or not self.step_impl_match:
            raise RadishError(
                "Unable to run Step '{} {}' because it has "
                "no Step Implementation assigned to it".format(self.keyword, self.text)
            )

        if self.state is not State.UNTESTED:
            raise RadishError(
                "Unable to run Step '{} {}' again. A Step can only be run exactly once.".format(
                    self.keyword, self.text
                )
            )

        args, kwargs = self.step_impl_match.evaluate()

        self.state = State.RUNNING
        try:
            if kwargs:
                self.step_impl.func(self, **kwargs)
            else:
                self.step_impl.func(self, *args)
        except Exception as exc:
            self.state = State.FAILED
            self.failure_report = StepFailureReport(exc)
        else:
            if self.state is State.RUNNING:
                self.state = State.PASSED
        return self.state
