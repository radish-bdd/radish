import re

from radish.stepregistry import step
from radish import when, then
from radish.terrain import world


@step(re.compile("I have the number in user data as (.+)"))
def have_number(step, input_variable):
    if world.config.user_data:
        if input_variable in world.config.user_data:
            step.context.numbers.append(int(world.config.user_data[input_variable]))
        else:
            msg = "Variable [{0}] is not in the user data (-u/--user-data) specified on the command-line."
            assert False, msg.format(input_variable)
    else:
        assert (
            False
        ), "There is no user data (-u/--user-data) specified on the command-line."


@when("I sum them")
def sum_numbers(step):
    step.context.result = sum(step.context.numbers)


@then(re.compile("I expect the result to be the value in user data as (.+)"))
def expect_result(step, result_variable):
    if world.config.user_data:
        if result_variable in world.config.user_data:
            assert step.context.result == int(world.config.user_data[result_variable])
        else:
            msg = "Variable [{0}] is not in the user data (-u/--user-data) specified on the command-line."
            assert False, msg.format(input_variable)
    else:
        assert (
            False
        ), "There is no user data (-u/--user-data) specified on the command-line."
