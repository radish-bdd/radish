# -*- coding: utf-8 -*-

from radish.stepregistry import step
from radish import given, when, then


@step("I have the following users")
def have_number(step):
    step.context.users = step.table


@when("I add them to the database")
def sum_numbres(step):
    for user in step.context.users:
        step.context.database.users.append(
            {
                "forename": user["forename"],
                "surname": user["surname"],
                "hero": user["hero"],
            }
        )


@then("I expect {number:g} users in the database")
def expect_result(step, number):
    assert len(step.context.database.users) == number
