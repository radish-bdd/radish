# -*- coding: utf-8 -*-

from radish.stepregistry import step
from radish import when


@step("I have the number {number:g}")
def have_number(step, number):
    step.context.numbers.append(number)


@when("I sum them")
def sum_numbers(step):
    step.context.result = sum(step.context.numbers)
