# -*- coding: utf-8 -*-

from radish.stepregistry import step
from radish import given, when, then


@step("I have the number {number:g}")
def have_number(step, number):
    step.context.numbers.append(number)


@when("I multiply them")
def sum_numbres(step):
    step.context.result = step.context.numbers[0] * step.context.numbers[1]


@then("I expect the result to be {result:g}")
def expect_result(step, result):
    assert step.context.result == result
