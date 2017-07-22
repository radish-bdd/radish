# -*- coding: utf-8 -*-

from radish.stepregistry import step
from radish import given, when, then

@step("I have the following quote")
def have_quote(step):
    step.context.quote = step.text

@when("I add it to the database")
def add_quote_to_db(step):
        step.context.database.quotes.append(step.context.quote)

@then("I expect {number:g} quote in the database")
def expect_amount_of_quotes(step, number):
    assert len(step.context.database.quotes) == number
