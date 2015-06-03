# -*- coding: utf-8 -*-

from radish.step import step


@step(r"I have the number \d+")
def have_number(number):
    pass


@step(r"I add \d+ to my number")
def add_to_number(addition):
    pass


@step(r"I expect the number to be 7")
def expect_number(number):
    pass
