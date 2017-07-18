# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""


from radish import given, when, then


@given('I have a step')
def have_a_step(step):
    "Given I have a step"
    pass


@when('I do something')
def do_something(step):
    "When I do something"
    pass


@then('I expect something')
def expect_something(step):
    "Then I expect something"
    pass
