# -*- coding: utf-8 -*-

from radish.terrain import world
from radish.stepregistry import step

world.number = 0


@step(r"I have the number (\d+)")
def have_number(step, number):
    world.number = int(number)


@step(r"I add (\d+) to my number")
def add_to_number(step, addition):
    world.number += int(addition)
    if int(addition) == 3:
        world.number += 1
    if int(addition) == 32:
        assert False, "SOME FAILURE"
    if int(addition) == 11:
        assert False, "ANTOHER ERROR"


@step(r"I expect the number to be (\d+)")
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
