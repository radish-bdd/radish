# -*- coding: utf-8 -*-

from radish import before


@before.each_scenario
def init_numbers(scenario):
    scenario.context.users = []
    scenario.context.database = lambda: None
    setattr(scenario.context.database, "users", [])
    scenario.context.database.users = []
