# -*- coding: utf-8 -*-

from radish import before


@before.each_scenario
def init_numbers(scenario):
    scenario.context.quote = None
    scenario.context.database = lambda: None
    setattr(scenario.context.database, "quotes", [])
    scenario.context.database.quotes = []
