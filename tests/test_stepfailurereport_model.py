"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

from radish.errors import RadishError
from radish.models.stepfailurereport import StepFailureReport


def test_stepfailurereport_model_should_correctly_analyse_a_exception():
    """The StepFailureReport model should correctly analyse a given Exception"""
    # given
    def raise_exc():
        raise RadishError("buuh!")

    raised_exception = None
    try:
        raise_exc()
    except RadishError as exc:
        # when
        report = StepFailureReport(exc)
        raised_exception = exc

    # then
    assert report.exception is raised_exception
    assert report.reason == "buuh!"
    assert report.name == "RadishError"
