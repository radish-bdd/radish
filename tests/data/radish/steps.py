# -*- coding: utf-8 -*-

from radish.step import step
from radish.terrain import world

world.number = 0


@step(r"I have the number (\d+)")
def have_number(step, number):
    world.number = int(number)


@step(r"I add (\d+) to my number")
def add_to_number(step, addition):
    world.number += int(addition)
    if int(addition) == 3:
        world.number += 1


@step(r"I expect the number to be (\d+)")
def expect_number(step, number):
    assert world.number == int(number), "Expected number to be {}. Actual number is: {}".format(number, world.number)
