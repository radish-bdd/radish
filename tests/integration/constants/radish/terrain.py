# -*- coding: utf-8 -*-

from radish import before

@before.each_scenario
def init_numbers(scenario):
    scenario.context.numbers = []
