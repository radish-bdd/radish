# -*- coding: utf-8 -*-

from radish import step, given, when, then


@step("a user named {:w}")
def have_user(step, username):
    # print(step.context)
    step.context.users[username] = {"site": None}


@step("a personal site owned by {username:w}")
def have_personal_site(step, username):
    # print(step.context)
    step.context.users[username]["site"] = {"access": []}


@step("{username:w} grants access to {consumer:w}")
def grant_personal_site_access(step, username, consumer):
    # print(step.context)
    step.context.users[username]["site"]["access"].append(consumer)


@when("I'm logged in as {username:w}")
def logged_in(step, username):
    # print(step.context)
    step.context.current_user = username


@then("I can access {username:w} personal site")
def can_access_personal_site(step, username):
    # print(step.context)
    assert step.context.current_user in step.context.users[username]["site"]["access"]


@then("I cannot access {username:w} personal site")
def cannot_access_personal_site(step, username):
    # print(step.context)
    assert (
        step.context.current_user not in step.context.users[username]["site"]["access"]
    )
