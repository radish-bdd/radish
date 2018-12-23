# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""


from radish import step


@step("Gegeben sei etwas")
def have_a_step(step):
    "Given I have a step"
    pass


@step("Wenn ich etwas mache")
def do_something(step):
    "When I do something"
    pass


@step("Dann erwarte ich etwas")
def expect_something(step):
    "Then I expect something"
    pass
