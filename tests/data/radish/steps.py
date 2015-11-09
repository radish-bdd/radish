# -*- coding: utf-8 -*-

from radish.terrain import world
from radish.stepregistry import step
from radish.argexpregistry import arg_expr, ArgumentExpression

world.number = 0

@step(ArgumentExpression("I have the number {number:g}"))
def have_number(step, number):
    world.number = int(number)


@step(r"I add (\d+) to my number")
def add_to_number(step, addition):
    world.number += int(addition)
    if int(addition) == 3:
        world.number += 1
    if int(addition) == 11:
        assert False, "ANTOHER ERROR °"


@step(ArgumentExpression("I expect the number to be {:MathExpression}"))
def expect_number(step, number):
    assert world.number == int(number), "Expected number to be {}. Actual number is: {}".format(number, world.number)


@step(r"I prepare users in world object")
def prepare_users(step):
    world.users = None
    #assert False, "Some bug"


@step(r"I initialize users in world object")
def init_users(step):
    world.users = []


@step(r"I setup the database")
def setup_database(step):
    step.behave_like("I prepare users in world object")
    step.behave_like("I initialize users in world object")


@step(r"I add the users")
def add_user(step):
    for row in step.table:
        world.users.append({"forename": row[0], "surname": row[1], "email": row[2]})


@step(r"I expect the user \"(.*?)\" in the database")
def expect_user_in_database(step, name):
    forename, surname = name.split()
    assert any(u for u in world.users if u["forename"] == forename and u["surname"] == surname), "No such user in the db"


@step(ArgumentExpression("I have the numeric expression {expression:MathExpression}"))
def have_expression(step, expression):
    world.result = expression


@step(ArgumentExpression("I add {addition:MathExpression} to this"))
def add_to_result(step, addition):
    world.result += addition


@step(ArgumentExpression("I expect the result to be {result:MathExpression}"))
def expect_result(step, result):
    assert world.result == result, "Result is {} but expected {}".format(world.result, result)


@step(ArgumentExpression("I have the float number {:FloatNumber}"))
def have_float_number(step, number):
    world.float_number = number


@step(ArgumentExpression("I add to my float number {:FloatNumber}"))
def add_to_float_number(step, number):
    world.float_number += number


@step(ArgumentExpression("I expect the float result to be {result:FloatNumber}"))
def expect_float_number(step, result):
    assert world.float_number == result, "Result is {} but expected {}".format(world.float_number, result)


@step("I have the following data:")
def have_data(step):
    step.context.some_data = step.text


@step("I ignore this step")
def ignore_step(step):
    pass


@step(ArgumentExpression("I expect the data to be \"{}\""))
def expect_data(step, expected_data):
    assert step.context.some_data == expected_data, "Data is: '{}'. Expected was: '{}'".format(step.context.some_data, expected_data)

@step("Given I install the database server")
def demo(step):
    pass


@step("When I add all default users")
def demo(step):
    pass


@step("And I add all default types")
def demo(step):
    pass


@step("And I initialize the database error handlers")
def demo(step):
    pass


@step("And I set the permissions for the administrator tables")
def demo(step):
    pass


@step("And I index imported fields")
def demo(step):
    pass


@step("Then I expect my installation to be complete")
def demo(step):
    pass

@step("I add the user \"Timo furrer\"")
def demo(step):
    pass


@step("I expect the user \"Timo Furrer\" in the databas")
def demo(step):
    pass
