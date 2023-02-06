# -*- coding: utf-8 -*-

from radish.stepregistry import step
from radish import when, then


@step("I have the number {number:g}")
def have_number(step, number):
    step.context.numbers.append(number)


@when("I divide them")
def sum_numbres(step):
    step.context.result = step.context.numbers[0] / step.context.numbers[1]


@then("I expect the result to be {result:g}")
def expect_result(step, result):
    assert step.context.result == result


@step("I have following numbers")
def have_numbers(step):
    for parameter in step.text.split(","):
        num = int(parameter.split(":")[1])
        step.context.numbers.append(num)


@then("I expect the result")
def expect_result(step):
    result = int(step.text.split(":")[1])
    assert step.context.result == result
