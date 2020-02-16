"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import base64

import radish.utils as utils
from radish.errors import RadishError, StepBehaveLikeRecursionError
from radish.models.state import State
from radish.models.stepfailurereport import StepFailureReport
from radish.models.timed import Timed


class Step(Timed):
    """Respresents a single instance of a Gherkin Step"""

    def __init__(
        self,
        step_id: int,
        keyword: str,
        used_keyword: str,
        text: str,
        doc_string,
        data_table,
        path: str,
        line: int,
    ) -> None:
        super().__init__()
        self.id = step_id
        self.keyword = keyword
        self.used_keyword = used_keyword
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

        #: Holds the behave-like runner
        self._behave_like_runner = None

        #: Holds information about the State of this Step
        self.state = State.UNTESTED
        self.failure_report = None

        #: Holds user-defined embeddings for this Step
        self.embeddings = []

    def __repr__(self) -> str:
        return "<Step: {id} '{keyword} {text}' @ {path}:{line}>".format(
            id=self.id,
            keyword=self.keyword,
            text=self.text,
            path=self.path,
            line=self.line,
        )  # pragma: no cover

    def set_feature(self, feature):
        """Set the Feature for this Step"""
        self.feature = feature  # pragma: no cover

    def set_rule(self, rule):
        """Set the Rule for this Step"""
        self.rule = rule  # pragma: no cover

    def set_scenario(self, scenario):
        """Set the Scenario for this Step"""
        self.scenario = scenario

    @property
    def context(self):
        """Return the Context object where this Step is running in"""
        return self.scenario.context

    def get_all_tags(self):
        """Return all Tags for this Step

        These Tags include the ones inherited from the Scenario and Feature.
        """
        return self.scenario.get_all_tags()

    def assign_implementation(self, step_impl, match):
        """Assign a matched Step Implementation to this Step"""
        self.step_impl = step_impl
        self.step_impl_match = match

    def __validate_if_runnable(self):
        """Validate if this Step is able to run

        If it's not able to run an Exception is raised.
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

    def with_behave_like_runner(func):
        def __wrapper(self, behave_like_runner, *args, **kwargs):
            self._behave_like_runner = behave_like_runner
            try:
                return func(self, *args, **kwargs)
            finally:
                self._behave_like_runner = None

        return __wrapper

    @with_behave_like_runner
    def run(self):
        """Run this Step

        The Step will only run if a ``StepImpl`` was assigned using ``assign_implementation``.
        """
        self.__validate_if_runnable()
        args, kwargs = self.step_impl_match.evaluate()

        self.state = State.RUNNING
        try:
            if kwargs:
                self.step_impl.func(self, **kwargs)
            else:
                self.step_impl.func(self, *args)
        except Exception as exc:
            self.fail(exc)
        else:
            if self.state is State.RUNNING:
                self.state = State.PASSED
        return self.state

    @with_behave_like_runner
    def debug(self):
        """Run this Step in a debugger"""
        self.__validate_if_runnable()
        args, kwargs = self.step_impl_match.evaluate()

        pdb = utils.get_debugger()

        self.state = State.RUNNING
        try:
            pdb.runcall(self.step_impl.func, self, *args, **kwargs)
        except Exception as exc:
            self.fail(exc)
        else:
            if self.state is State.RUNNING:
                self.state = State.PASSED
        return self.state

    def behave_like(self, step_line):
        """Run this Step as if it would be the one given in ``step_line``

        This function requires ``self._behave_like_runner`` to be set.
        """
        if self._behave_like_runner is None:
            raise RadishError(
                "This Step is unable to use the `behave_like`-Feature because no runner is provided"
            )

        state, step = self._behave_like_runner(step_line)
        if state is State.FAILED:
            try:
                raise step.failure_report.exception
            except RecursionError:
                raise StepBehaveLikeRecursionError()

    def fail(self, exception):
        """Let this Step fail with the given exception"""
        self.state = State.FAILED
        self.failure_report = StepFailureReport(exception)

    def skip(self):
        """Skip this Step

        This method is supposed to be called from Step Implementations.
        """
        if self.state is not State.RUNNING:
            raise RadishError("Steps can only be skipped when they run")
        self.state = State.SKIPPED

    def pending(self):
        """Mark this Step as pending

        All pending Steps will be reminded about in the Runs summary.

        This method is supposed to be called from Step Implementations.
        """
        if self.state is not State.RUNNING:
            raise RadishError("Steps can only be marked as pending when they run")
        self.state = State.PENDING

    def embed(self, data, mime_type="text/plain", encode_data_to_base64=True):
        """Embed data into Step
            - step embedded data can be used for cucumber json reports
            - allow to attach text, html or images

        This method is supposed to be called from Step Implementations.

        :param data: data attached to report
            data needs to be encoded in base64 for proper handling by tests reporting tools
            if not encoded in base64 encoded_data_to_base64 needs to be True (default value)
        :param mime_type: image/png, image/bmp, text/plain, text/html
            - mime types with special support by Cucumber reporting
            - other mime types will be handled with default handling
        :param encode_data_to_base64: encode data to base64 if True
        """
        if encode_data_to_base64:
            data = base64.standard_b64encode(data.encode()).decode()
        self.embeddings.append({"data": data, "mime_type": mime_type})
