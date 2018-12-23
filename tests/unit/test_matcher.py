# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import re

import pytest

from parse_type.cfparse import Parser

import radish.matcher as matcher
import radish.exceptions as errors


@pytest.mark.parametrize(
    "regex, string, expected_args, expected_kwargs",
    [
        (r"Given I have the number (\d+)", "Given I have the number 5", ("5",), {}),
        (
            r"Given I have the number (?P<number>\d+)",
            "Given I have the number 5",
            ("5",),
            {"number": "5"},
        ),
        (
            r"Given I have the number (?P<number>\d+) and (\d+)",
            "Given I have the number 4 and 2",
            ("4", "2"),
            {"number": "4"},
        ),
    ],
    ids=[
        "Regex with unnamed groups",
        "Regex with named groups",
        "Regex with unnamed and named groups",
    ],
)
def test_regex_step_arguments_object(regex, string, expected_args, expected_kwargs):
    """
    Test functionality of RegexStepArguments object
    """
    # given
    match = re.search(regex, string)
    args = matcher.RegexStepArguments(match)

    # when
    actual_args, actual_kwargs = args.evaluate()

    # then
    assert actual_args == expected_args
    assert actual_kwargs == expected_kwargs


@pytest.mark.parametrize(
    "parse_pattern, string, expected_args, expected_kwargs",
    [
        ("Given I have the number {:d}", "Given I have the number 5", (5,), {}),
        (
            "Given I have the number {number:d}",
            "Given I have the number 5",
            tuple(),
            {"number": 5},
        ),
        (
            "Given I have the number {number:d} and {:d}",
            "Given I have the number 4 and 2",
            (2,),
            {"number": 4},
        ),
    ],
    ids=[
        "Parse Pattern with unnamed groups",
        "Parse Pattern with named groups",
        "Parse Pattern with unnamed and named groups",
    ],
)
def test_parse_step_arguments_object(
    parse_pattern, string, expected_args, expected_kwargs
):
    """
    Test functionality of ParseStepArguments object
    """
    # given
    parser = Parser(parse_pattern)
    match = parser.search(string, evaluate_result=False)
    args = matcher.ParseStepArguments(match)

    # when
    actual_args, actual_kwargs = args.evaluate()

    # then
    assert actual_args == expected_args
    assert actual_kwargs == expected_kwargs


@pytest.mark.parametrize(
    "given_sentence, given_steps, expected_argument_match_type, expected_func_match",
    [
        (
            "Given I have a number",
            {re.compile("Given I have a number"): 1},
            matcher.RegexStepArguments,
            1,
        ),
        (
            "Given I have a number to test",
            {re.compile("Given I have a number"): 1},
            matcher.RegexStepArguments,
            1,
        ),
        (
            "Given I have a number",
            {
                re.compile("Given I have some number"): 1,
                re.compile("Given I have a number"): 2,
            },
            matcher.RegexStepArguments,
            2,
        ),
        (
            "Given I have a number",
            {re.compile("I have a number"): 1, re.compile("Given I have a number"): 2},
            matcher.RegexStepArguments,
            2,
        ),
        (
            "Given I have the number 5",
            {
                re.compile(r"I have the number (\d+)"): 1,
                re.compile(r"Given I have the number (\d+)"): 2,
            },
            matcher.RegexStepArguments,
            2,
        ),
        (
            "Given I have the number 5 which I use to test",
            {
                re.compile(
                    r"Given I have the number (\d+) which I use to do some stuff"
                ): 1,
                re.compile(r"Given I have the number (\d+) which I use"): 2,
            },
            matcher.RegexStepArguments,
            2,
        ),
        # Parse Argument Matches
        (
            "Given I have a number",
            {"Given I have a number": 1},
            matcher.ParseStepArguments,
            1,
        ),
        (
            "Given I have a number to test",
            {"Given I have a number": 1},
            matcher.ParseStepArguments,
            1,
        ),
        (
            "Given I have a number",
            {"Given I have some number": 1, "Given I have a number": 2},
            matcher.ParseStepArguments,
            2,
        ),
        (
            "Given I have a number",
            {"I have a number": 1, "Given I have a number": 2},
            matcher.ParseStepArguments,
            2,
        ),
        (
            "Given I have the number 5",
            {"I have the number {:d}": 1, "Given I have the number {:d}": 2},
            matcher.ParseStepArguments,
            2,
        ),
        (
            "Given I have the number 5 which I use to test",
            {
                "Given I have the number {:d} which I use to do some stuff": 1,
                "Given I have the number {:d} which I use": 2,
            },
            matcher.ParseStepArguments,
            2,
        ),
    ],
    ids=[
        "Regex: match simple step with single candidate",
        "Regex: match simple step with single candidate which is not a perfect match",
        "Regex: match simple step with one matching candidate",
        "Regex: match simple step with multiple candidate - best match",
        "Regex: match step with args with multiple candidate - best match",
        "Regex: match step with args with multiple candidate - closest match",
        # Parse Argument Matches
        "Parse: match simple step with single candidate",
        "Parse: match simple step with single candidate which is not a perfect match",
        "Parse: match simple step with one matching candidate",
        "Parse: match simple step with multiple candidate - best match",
        "Parse: match step with args with multiple candidate - best match",
        "Parse: match step with args with multiple candidate - closest match",
    ],
)
def test_match_sentence_with_steps(
    given_sentence, given_steps, expected_argument_match_type, expected_func_match
):
    """
    Test matching a sentence with given Steps
    """
    # given & when
    match = matcher.match_step(given_sentence, given_steps)

    # then
    assert isinstance(match.argument_match, expected_argument_match_type)
    assert match.func == expected_func_match


@pytest.mark.parametrize(
    "given_sentence, given_steps",
    [
        ("Given I have the number", {re.compile("Given I have a number"): 1}),
        ("Given I have the number foo", {re.compile(r"Given I have number (\d+)"): 1}),
        ("Given I have the number", {"Given I have a number": 1}),
        ("Given I have the number foo", {"Given I have number {:d}": 1}),
    ],
    ids=[
        "Regex: simple not matching step",
        "Regex: not matching step with arguments",
        "Parse: simple not matching step",
        "Parse: not matching step with arguments",
    ],
)
def test_no_step_match(given_sentence, given_steps):
    """
    Test failing to match a sentence with given Steps
    """
    # given & when
    match = matcher.match_step(given_sentence, given_steps)

    # then
    assert match is None


def test_invalid_parse_pattern():
    """
    Test failure for invalid Parse pattern
    """
    # given
    invalid_pattern = "Given I have the number {:d {}"

    # when
    with pytest.raises(errors.StepPatternError) as exc:
        matcher.match_step("Given I have the number 5", {invalid_pattern: int})

    assert str(exc.value).startswith(
        "Cannot compile pattern 'Given I have the number {:d {}' of step 'int': "
    )


@pytest.mark.parametrize(
    "given_sentence, given_steps, expected_func, expected_args, expected_kwargs",
    [
        (
            "Given I have a number",
            {re.compile(r"Given I have a number"): 1},
            1,
            tuple(),
            {},
        ),
        (
            "Given I have the number 4 and 2",
            {re.compile(r"Given I have the number (?P<number>\d+) and (\d+)"): 1},
            1,
            ("4", "2"),
            {"number": "4"},
        ),
        ("Given I have a number", {"Given I have a number": 1}, 1, tuple(), {}),
        (
            "Given I have the number 4 and 2",
            {"Given I have the number {number:d} and {:d}": 1},
            1,
            (2,),
            {"number": 4},
        ),
    ],
    ids=[
        "Regex: simple step merge",
        "Regex: step merge with arguments",
        "Parse: simple step merge",
        "Parse: step merge with arguments",
    ],
)
def test_merging_step(
    given_sentence, given_steps, expected_func, expected_args, expected_kwargs, mocker
):
    """
    Test merging a Step with registered Step functions
    """
    # given
    step_to_merge = mocker.MagicMock(
        context_sensitive_sentence=given_sentence,
        definition_func=None,
        argument_match=None,
    )

    # when
    matcher.merge_step(step_to_merge, given_steps)
    actual_args, actual_kwargs = step_to_merge.argument_match.evaluate()

    # then
    assert step_to_merge.definition_func == expected_func
    assert actual_args == expected_args
    assert actual_kwargs == expected_kwargs


@pytest.mark.parametrize(
    "given_sentence, given_steps",
    [
        ("Given I have the number", {re.compile("Given I have a number"): 1}),
        ("Given I have the number foo", {re.compile(r"Given I have number (\d+)"): 1}),
        ("Given I have the number", {"Given I have a number": 1}),
        ("Given I have the number foo", {"Given I have number {:d}": 1}),
    ],
    ids=[
        "Regex: simple not matching step",
        "Regex: not matching step with arguments",
        "Parse: simple not matching step",
        "Parse: not matching step with arguments",
    ],
)
def test_no_step_definition_merge(given_sentence, given_steps, mocker):
    """
    Test failure when no Step definition function can be found during Step merge
    """
    # given
    step_to_merge = mocker.MagicMock(
        context_sensitive_sentence=given_sentence,
        definition_func=None,
        argument_match=None,
    )

    # when
    with pytest.raises(errors.StepDefinitionNotFoundError) as exc:
        matcher.merge_step(step_to_merge, given_steps)

    # then
    assert str(exc.value).startswith("Cannot find step definition for step")
