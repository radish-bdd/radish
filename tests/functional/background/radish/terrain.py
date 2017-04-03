# -*- coding: utf-8 -*-

from radish import before


@before.each_scenario
def before_scenario(scenario):
    # print(scenario.context)
    scenario.context.users = {}
    scenario.context.current_user = None
