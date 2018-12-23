# -*- coding: utf-8 -*-

from radish import given, when, then
from radish import world

from example.model import Hero


@given("I setup the hero database")
def setup_hero_db(step):
    pass


@when("I query for the hero with name {hero:Hero}")
def query_hero(step, hero):
    step.context.last_queried_hero = hero


@then("I expect it's name to be {forename:w} {surname:w}")
def expect_hero(step, forename, surname):
    assert step.context.last_queried_hero.forename == forename
    assert step.context.last_queried_hero.surname == surname
