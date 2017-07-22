# -*- coding: utf-8 -*-

from radish import before
from radish import world
from radish import custom_type


@before.each_scenario
def setup_hero_db(scenario):
    world.heros = []


@custom_type("Hero", r"[A-Z][a-z]+")
def get_hero_custom_type(text):
    """
    Return a hero object by the given name
    """
    for hero in world.heros:
        if hero.heroname == text:
            return hero

    return None
