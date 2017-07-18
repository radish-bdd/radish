# -*- coding: utf-8 -*-

import re

from radish.stepregistry import step
from radish import given, when, then


# @step(re.compile(r"I have the number (\d+)"))
@step("I have the number {number:g}")
def have_number(step, number):
    step.context.numbers.append(int(number))


@when("I sum them")
def sum_numbers(step):
    step.context.result = sum(step.context.numbers)


@then("I expect the result to be {result:g}")
def expect_result(step, result):
    assert step.context.result == result
