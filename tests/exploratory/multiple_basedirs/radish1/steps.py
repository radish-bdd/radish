from radish import when
from radish.stepregistry import step


@step("I have the number {number:g}")
def have_number(step, number):
    step.context.numbers.append(number)


@when("I sum them")
def sum_numbers(step):
    step.context.result = sum(step.context.numbers)
