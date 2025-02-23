import re

from radish import then, when
from radish.stepregistry import step


@step("I have the number {number:g}")
def have_number(step, number):
    step.context.numbers.append(number)


@step(re.compile("I have the numbers (.*)"))
def have_numbers(step, numbers):
    numbers = [x.strip() for x in numbers.split(",")]

    for n in numbers:
        step.behave_like("I have the number {0}".format(n))


@when("I sum them")
def sum_numbers(step):
    step.context.result = sum(step.context.numbers)


@then("I expect the result to be {result:g}")
def expect_result(step, result):
    assert step.context.result == result
