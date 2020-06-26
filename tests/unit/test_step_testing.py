"""
radish
~~~~~~

The root from red to green. BDD tooling for Python.

:copyright: (c) 2019 by Timo Furrer <tuxtimo@gmail.com>
:license: MIT, see LICENSE for more details.
"""

import re
import textwrap

# NOTE(TF): we need the OrderedDict for Python 3.5 test reproducibility.
from collections import OrderedDict

import pytest

from radish.errors import RadishError, StepImplementationNotFoundError
from radish.models import Step
from radish.step_testing.matcher import (
    assert_step_arguments,
    assert_step_match,
    assert_step_not_match,
    parse_matcher_config,
    print_failure,
)
from radish.stepregistry import StepRegistry


def create_matcher_config_file(tmp_path, contents):
    """Helper function to create a matcher config file from a string"""
    tmp_matcher_path = tmp_path / "matcher_config.yml"
    with tmp_matcher_path.open("w", encoding="utf-8") as tmp_matcher_file:
        tmp_matcher_file.write(textwrap.dedent(contents))

    return tmp_matcher_path


def test_parse_config_should_fail_if_step_key_not_present(tmp_path):
    # GIVEN
    matcher_config_path = create_matcher_config_file(
        tmp_path,
        """
        - not-step: step text

        - not-step: step text
        """,
    )

    # THEN
    with pytest.raises(
        RadishError, match="All Matcher Config must start with the 'step' key"
    ):
        # WHEN
        parse_matcher_config(matcher_config_path)


def test_parse_config_should_fail_if_should_match_keys_not_present(tmp_path):
    # GIVEN
    matcher_config_path = create_matcher_config_file(
        tmp_path,
        """
        - step: step text
        """,
    )

    # THEN
    with pytest.raises(
        RadishError,
        match=(
            "Each Matcher Config must either contain "
            "a 'should_match' or 'should_not_match' key"
        ),
    ):
        # WHEN
        parse_matcher_config(matcher_config_path)


def test_parse_config_should_fail_if_should_match_key_and_should_match_present(
    tmp_path,
):
    # GIVEN
    matcher_config_path = create_matcher_config_file(
        tmp_path,
        """
        - step: step text
          should_match: step func
          should_not_match: step func
        """,
    )

    # THEN
    with pytest.raises(
        RadishError,
        match=(
            "Each Matcher Config must either contain "
            "a 'should_match' or 'should_not_match' key"
        ),
    ):
        # WHEN
        parse_matcher_config(matcher_config_path)


def test_parse_config_should_pass_if_should_match_key_not_and_should_not_match_present(
    tmp_path,
):
    # GIVEN
    matcher_config_path = create_matcher_config_file(
        tmp_path,
        """
        - step: step text
          should_not_match: step func
        """,
    )

    # WHEN
    match_config = parse_matcher_config(matcher_config_path)

    # THEN
    assert match_config[0]["should_not_match"] == "step func"


def test_parse_config_should_pass_if_should_not_match_key_not_and_should_match_present(
    tmp_path,
):
    # GIVEN
    matcher_config_path = create_matcher_config_file(
        tmp_path,
        """
        - step: step text
          should_match: step func
        """,
    )

    # WHEN
    match_config = parse_matcher_config(matcher_config_path)

    # THEN
    assert match_config[0]["should_match"] == "step func"


def test_parse_config_should_pass_if_with_arguments_is_specified(tmp_path):
    # GIVEN
    matcher_config_path = create_matcher_config_file(
        tmp_path,
        """
        - step: step text
          should_match: step func
          with_arguments:
            - foo: bar
        """,
    )

    # WHEN
    match_config = parse_matcher_config(matcher_config_path)

    # THEN
    assert match_config[0]["with_arguments"] == [{"foo": "bar"}]


def test_parse_config_should_fail_for_invalid_keys(tmp_path):
    # GIVEN
    matcher_config_path = create_matcher_config_file(
        tmp_path,
        """
        - step: step text
          should_match: step func
          invalid_key: x
          another_invalid_key: y
        """,
    )

    # THEN
    with pytest.raises(
        RadishError,
        match=(
            "All Matcher Config only allow the keys: "
            "should_match, should_not_match, step, with_arguments. "
            "The following are not allowed: another_invalid_key, invalid_key."
        ),
    ):
        # WHEN
        parse_matcher_config(matcher_config_path)


def test_print_failure_should_output_only_red_cross_if_no_func_and_no_errors(capsys):
    # GIVEN
    expected_output = "✘ \n"

    # WHEN
    print_failure(None, [])
    actual_output = capsys.readouterr().out

    # THEN
    assert actual_output == expected_output


def test_print_failure_should_output_func_location(capsys):
    # GIVEN
    def func():
        pass

    expected_output = r"✘ \(at .*?test_step_testing.py:{}\)\n".format(
        func.__code__.co_firstlineno
    )

    # WHEN
    print_failure(func, [])
    actual_output = capsys.readouterr().out

    # THEN
    assert re.match(expected_output, actual_output)


def test_print_failure_should_output_specified_errors(capsys):
    # GIVEN
    errors = ["some error", "another error"]

    expected_output = "✘ \n  - some error\n  - another error\n"

    # WHEN
    print_failure(None, errors)
    actual_output = capsys.readouterr().out

    # THEN
    assert actual_output == expected_output


def test_assert_step_arguments_should_fail_if_expected_argument_is_not_present():
    # GIVEN
    actual_step_arguments = {"arg1": None, "arg2": None}
    expected_step_arguments = {"not-existing-arg": "value1"}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 1
    assert actual_errors[0] == (
        "Expected argument \"not-existing-arg\" is not in matched arguments ['arg1', 'arg2']"
    )


def test_assert_step_arguments_should_pass_if_arguments_match():
    # GIVEN
    actual_step_arguments = {"arg1": "value", "arg2": 2}
    expected_step_arguments = {"arg1": "value", "arg2": 2}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 0


def test_assert_step_arguments_should_fail_if_expected_argument_value_doesnt_match():
    # GIVEN
    actual_step_arguments = {"arg1": "value", "arg2": 2}
    expected_step_arguments = {"arg1": "not-correct-value", "arg2": 2}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 1
    assert actual_errors[0] == (
        'Expected argument "arg1" with value "not-correct-value" does not match value "value"'
    )


def test_assert_step_arguments_should_collect_all_argument_mismatched():
    # GIVEN
    actual_step_arguments = {"arg1": "value", "arg2": 2}
    expected_step_arguments = OrderedDict([("arg1", "not-correct-value"), ("arg2", -1)])

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 2
    assert actual_errors[0] == (
        'Expected argument "arg1" with value "not-correct-value" does not match value "value"'
    )
    assert actual_errors[1] == (
        'Expected argument "arg2" with value "-1" does not match value "2"'
    )


def test_assert_step_arguments_should_fail_if_argument_values_have_type_mismatch():
    # GIVEN
    actual_step_arguments = {"int-arg1": 42}
    expected_step_arguments = {"int-arg1": "42"}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 1
    assert actual_errors[0] == (
        'Expected argument "int-arg1" is of type "str" but should be "int"'
    )


def test_assert_step_arguments_should_correctly_compare_dicts():
    # GIVEN
    actual_step_arguments = {"dict-arg1": {"key1": 1, "key2": 2}}
    expected_step_arguments = {"dict-arg1": {"key1": 1, "key2": 2}}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 0


def test_assert_step_arguments_should_fail_if_dicts_dont_match():
    # GIVEN
    actual_step_arguments = {"dict-arg1": {"key1": 1, "key2": 2}}
    expected_step_arguments = {"dict-arg1": {"key1": 0, "key2": 0}}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 1


def test_assert_step_arguments_should_use_explcitly_specified_type_and_value():
    # GIVEN
    actual_step_arguments = {"str-arg1": "value"}
    expected_step_arguments = {"str-arg1": {"type": "str", "value": "value"}}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 0


def test_assert_step_arguments_should_use_repr_if_specified_along_with_explcit_type_and_value():
    # GIVEN
    actual_step_arguments = {"str-arg1": "value"}
    expected_step_arguments = {
        "str-arg1": {"use_repr": True, "type": "str", "value": "'value'"}
    }

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 0


def test_assert_step_arguments_should_fail_if_specified_value_has_not_explictly_specified_type():
    # GIVEN
    actual_step_arguments = {"str-arg1": "value"}
    expected_step_arguments = {"str-arg1": {"type": "str", "value": 42}}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 1
    assert actual_errors[0] == (
        "Conflicting argument configuration: "
        'given value is actually of type "int" although it should match a value of type "str"'
    )


def test_assert_step_arguments_should_use_specified_cast_for_explicit_value():
    # GIVEN
    actual_step_arguments = {"int-arg1": 42}
    expected_step_arguments = {"int-arg1": {"type": "int", "value": "42", "cast": True}}

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 0


def test_assert_step_arguments_should_fail_if_type_is_not_known_for_cast():
    # GIVEN
    actual_step_arguments = {"int-arg1": 42}
    expected_step_arguments = {
        "int-arg1": {"type": "UnknownType", "value": "42", "cast": True}
    }

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 1
    assert actual_errors[0] == (
        'Cannot cast to type "UnknownType" because it is unknown'
    )


def test_assert_step_arguments_should_fail_if_unable_to_cast():
    # GIVEN
    actual_step_arguments = {"int-arg1": 42}
    expected_step_arguments = {
        "int-arg1": {"type": "int", "value": "not-an-int", "cast": True}
    }

    # WHEN
    actual_errors = assert_step_arguments(
        actual_step_arguments, expected_step_arguments
    )

    # THEN
    assert len(actual_errors) == 1
    assert actual_errors[0] == ('Failed to cast "not-an-int" to given type "int"')


def test_assert_step_not_match_should_pass_if_the_step_doesnt_match_any(mocker):
    # GIVEN
    step = mocker.MagicMock(name="Step", spec=Step, text="Step", keyword="")
    step_registry = mocker.MagicMock(name="StepRegistry", spec=StepRegistry)

    matcher_mock = mocker.patch("radish.step_testing.matcher.matcher")
    matcher_mock.match_step.side_effect = StepImplementationNotFoundError(step)

    # WHEN
    step_not_found = assert_step_not_match(step, "some_step_func", step_registry)

    # THEN
    assert step_not_found is True


def test_assert_step_not_match_should_pass_if_the_step_doesnt_match_correct_step(
    mocker,
):
    # GIVEN
    def some_step_impl(step):
        pass

    step = mocker.MagicMock(name="Step")
    step.step_impl.func = some_step_impl
    step_registry = mocker.MagicMock(name="StepRegistry", spec=StepRegistry)

    mocker.patch("radish.step_testing.matcher.matcher")

    # WHEN
    step_not_found = assert_step_not_match(step, "some_step_func", step_registry)

    # THEN
    assert step_not_found is True


def test_assert_step_not_match_should_fail_if_matches_correct_step_impl(mocker):
    # GIVEN
    def some_step_impl(step):
        pass

    step = mocker.MagicMock(name="Step")
    step.step_impl.func = some_step_impl
    step_registry = mocker.MagicMock(name="StepRegistry", spec=StepRegistry)

    mocker.patch("radish.step_testing.matcher.matcher")

    # WHEN
    step_not_found = assert_step_not_match(step, "some_step_impl", step_registry)

    # THEN
    assert step_not_found is False


def test_assert_step_match_should_pass_if_step_matches(mocker):
    # GIVEN
    def some_step_impl(step):
        pass

    step = mocker.MagicMock(name="Step")
    step.step_impl.func = some_step_impl
    step_registry = mocker.MagicMock(name="StepRegistry", spec=StepRegistry)

    mocker.patch("radish.step_testing.matcher.matcher")

    # WHEN
    step_match = assert_step_match(step, "some_step_impl", [], step_registry)

    # THEN
    assert step_match is True


def test_assert_step_match_should_fail_if_step_not_matches_any(mocker):
    # GIVEN
    step = mocker.MagicMock(name="Step")
    step_registry = mocker.MagicMock(name="StepRegistry", spec=StepRegistry)

    matcher_mock = mocker.patch("radish.step_testing.matcher.matcher")
    matcher_mock.match_step.side_effect = StepImplementationNotFoundError(step)

    # WHEN
    step_match = assert_step_match(step, "some_step_impl", [], step_registry)

    # THEN
    assert step_match is False


def test_assert_step_match_should_fail_if_step_not_matches_wrong_step(mocker):
    # GIVEN
    def some_step_impl(step):
        pass

    step = mocker.MagicMock(name="Step")
    step.step_impl.func = some_step_impl
    step_registry = mocker.MagicMock(name="StepRegistry", spec=StepRegistry)

    mocker.patch("radish.step_testing.matcher.matcher")

    # WHEN
    step_match = assert_step_match(step, "another_step_impl", [], step_registry)

    # THEN
    assert step_match is False
