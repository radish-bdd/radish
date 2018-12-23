# -*- coding: utf-8 -*-

from radish import before


@before.each_scenario
def init_numbers(scenario):
    scenario.context.numbers = []


@before.each_scenario(on_tags="headstart")
def init_numbers_headstart(scenario):
    scenario.context.numbers.append(5)
