from example.model import Hero

from radish import before, custom_type, world

world.heros = [Hero("Peter", "Parker", "Spiderman"), Hero("Bruce", "Wayne", "Batman")]


@before.each_scenario
def setup_hero_db(scenario):
    pass


@custom_type("Hero", r"[A-Z][a-z]+")
def get_hero_custom_type(text):
    """
    Return a hero object by the given name
    """
    for hero in world.heros:
        if hero.heroname == text:
            return hero

    return None
