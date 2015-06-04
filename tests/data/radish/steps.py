# -*- coding: utf-8 -*-

from radish.step import step
from radish.terrain import world

world.number = 0


@step(r"I have the number (\d+)")
def have_number(number):
    world.number = number


@step(r"I add (\d+) to my number")
def add_to_number(addition):
    world.number += addition


@step(r"I expect the number to be (\d+)")
def expect_number(number):
    assert world.number == number, "Expected number to be {}. Actual number is: {}".format(number, world.number)
