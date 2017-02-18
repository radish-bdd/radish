# -*- coding: utf-8 -*-

from radish import given, when, then
from radish import world
from model import Hero


@given('I have the following heros in the database')
def have_number(step):
    world.heros = [Hero(*row) for row in step.table]


@when('I query for the hero with name {hero:Hero}')
def sum_numbres(step, hero):
    step.context.last_queried_hero = hero


@then('I expect it\'s name to be {forename:w} {surname:w}')
def expect_result(step, forename, surname):
    assert step.context.last_queried_hero.forename == forename
    assert step.context.last_queried_hero.surname == surname
