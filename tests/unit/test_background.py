# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""


from radish.background import Background
from radish.stepmodel import Step


def test_creating_simple_background():
    """
    Test creating a simple Background
    """
    # given & when
    background = Background(
        "Background", "I am a Background", "foo.feature", 1, parent=None
    )

    # then
    assert background.id is None
    assert background.keyword == "Background"
    assert background.sentence == "I am a Background"
    assert background.path == "foo.feature"
    assert background.line == 1
    assert background.parent is None


def test_creating_a_concrete_background_instance():
    """
    Test creating a concrete Background instance
    """
    # given & when
    background = Background(
        "Background", "I am a Background", "foo.feature", 1, parent=None
    )
    # add some Steps
    background.steps.append(Step(1, "Foo", "foo.feature", 2, background, False))
    background.steps.append(Step(2, "Foo", "foo.feature", 3, background, False))

    # when
    instance = background.create_instance()

    # then
    assert len(instance.steps) == 2
    assert background.steps[0] != instance.steps[0]
    assert background.steps[1] != instance.steps[1]
