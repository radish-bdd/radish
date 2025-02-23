from radish import then, when
from radish.stepregistry import step


@step("I have the number {number:g}")
def have_number(step, number):
    step.context.numbers.append(number)


@when("I sum them")
def sum_numbers(step):
    step.context.result = sum(step.context.numbers)


@then("I expect the result to be {result:g}")
def expect_result(step, result):
    assert step.context.result == result
