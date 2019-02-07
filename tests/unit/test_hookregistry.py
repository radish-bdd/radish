# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""

import pytest

from radish.model import Tag
from radish.hookregistry import before, after
import radish.exceptions as errors


def test_available_hooks():
    """
    Test that all expected hooks are available
    """
    # then
    assert callable(before.all)
    assert callable(after.all)

    assert callable(before.each_feature)
    assert callable(after.each_feature)

    assert callable(before.each_scenario)
    assert callable(after.each_scenario)

    assert callable(before.each_step)
    assert callable(after.each_step)


def test_registering_simple_hook(hookregistry):
    """
    Test registering simple hooks
    """
    # given & when
    @before.all
    def before_all_hook_legacy():
        pass

    @before.all()
    def before_all_hook():
        pass

    # then
    assert len(hookregistry.hooks["all"]["before"]) == 2


def test_call_hook(hookregistry, mocker):
    """
    Test calling registered hooks
    """
    # given
    @before.all()
    def before_all(features, stub):
        stub()

    @before.each_step()
    def before_each_step(step, stub):
        stub()

    hook_call_stub = mocker.stub()

    # when & then
    hookregistry.call("before", "all", True, mocker.MagicMock(), hook_call_stub)
    assert hook_call_stub.call_count == 1

    hookregistry.call("before", "each_step", True, mocker.MagicMock(), hook_call_stub)
    assert hook_call_stub.call_count == 2


def test_call_hook_exception(hookregistry, mocker):
    """
    Test calling registered hook which raises an exception
    """
    # given
    @before.all()
    def before_all(features):
        raise AssertionError("some error")

    # when
    with pytest.raises(errors.HookError) as exc:
        hookregistry.call("before", "all", True, mocker.MagicMock())

    # then
    assert exc.match(r".*AssertionError: some error")


def test_call_hooks_filtered_by_tags(hookregistry, mocker):
    """
    Test calling filtered hooks by tags
    """
    # given
    @after.all()
    def generic_cleanup(features, stub):
        stub()

    @after.all(on_tags="bad_case")
    def bad_case_cleanup(features, stub):
        stub()

    @after.all(on_tags="good_case")
    def good_case_cleanup(features, stub):
        stub()

    hook_call_stub = mocker.stub()
    model = mocker.MagicMock(all_tags=[])

    models = [
        mocker.MagicMock(all_tags=[Tag(name="good_case")]),
        mocker.MagicMock(all_tags=[Tag(name="bad_case")]),
    ]

    # when & then
    # all tags
    hookregistry.call("after", "all", True, model, hook_call_stub)
    assert hook_call_stub.call_count == 1

    # only generic & good case
    model.all_tags = [Tag(name="good_case")]
    hookregistry.call("after", "all", True, model, hook_call_stub)
    assert hook_call_stub.call_count == 3

    # only generic & bad case
    model.all_tags = [Tag(name="bad_case")]
    hookregistry.call("after", "all", True, model, hook_call_stub)
    assert hook_call_stub.call_count == 5

    # good case & bad case because of model list
    hookregistry.call("after", "all", True, models, hook_call_stub)
    assert hook_call_stub.call_count == 8


def test_call_before_hooks_in_correct_order(hookregistry, mocker):
    """
    Test calling registered hooks in the correct order
    """
    # given
    data = []  # used to capture ordering

    @before.all(order=2)
    def second_hook(features):
        data.append(2)

    @before.all(order=1)
    def first_hook(step):
        data.append(1)

    # when
    hookregistry.call("before", "all", True, mocker.MagicMock())

    # then
    assert data == [1, 2]


def test_call_after_hooks_in_correct_order(hookregistry, mocker):
    """
    Test calling registered hooks in the correct order
    """
    # given
    data = []  # used to capture ordering

    @after.all(order=2)
    def second_hook(features):
        data.append(2)

    @after.all(order=1)
    def first_hook(step):
        data.append(1)

    # when
    hookregistry.call("after", "all", False, mocker.MagicMock())

    # then
    assert data == [2, 1]
