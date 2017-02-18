# -*- coding: utf-8 -*-

from radish import before
from radish import world
from radish import arg_expr


@before.each_scenario
def setup_hero_db(scenario):
    world.heros = []


@arg_expr("Hero", r"[A-Z][a-z]+")
def get_hero_arg_expr(text):
    """
    Return a hero object by the given name
    """
    for hero in world.heros:
        if hero.heroname == text:
            return hero

    return None
