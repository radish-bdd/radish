import re

from radish import then, when
from radish.stepregistry import step


@step(re.compile(r"I have the number ([0-9]+)"))
def have_number(step, number):
    step.context.numbers.append(float(number))


@when(re.compile(r"I sum them"))
def sum_numbers(step):
    step.context.result = sum(step.context.numbers)


@then(re.compile(r"I expect the result to be (\d+)"))
def expect_result(step, result):
    assert step.context.result == float(result)
