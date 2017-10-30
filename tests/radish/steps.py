# -*- coding: utf-8 -*-

"""
    radish
    ~~~~~~

    Behavior Driven Development tool for Python - the root from red to green

    Copyright: MIT, Timo Furrer <tuxtimo@gmail.com>
"""


from radish import given, when, then


@given('I have a step')
def have_a_step(step):
    "Given I have a step"
    pass


@when('I do something')
def do_something(step):
    "When I do something"
    pass


@then('I expect something')
def expect_something(step):
    "Then I expect something"
    pass


@given('I have the number {number:d}')
def have_number(step, number):
    "Given I have the number <n>"
    if not hasattr(step.context, 'numbers'):
        step.context.numbers = []

    step.context.numbers.append(number)


@when('I add them up')
def sum_numbers(step):
    "When I add them up"
    step.context.sum = sum(step.context.numbers)


@when('I add them up with failure')
def sum_numbers(step):
    "When I add them up with failure"
    assert False, 'Unable to add numbers: {0}'.format(step.context.numbers)


@when('I subtract them')
def subtract_numbers(step):
    "When I subtract them up"
    difference = step.context.numbers[0]
    for n in step.context.numbers[1:]:
        difference -= n
    step.context.difference = difference


@then('I expect the sum to be {expected_sum:d}')
def expect_sum(step, expected_sum):
    "Then I expect the sum to be <n>"
    assert step.context.sum == expected_sum, 'The expected sum {0} does not match actual sum {1}'.format(
        expected_sum, step.context.sum)


@then('I expect the difference to be {expected_diff:d}')
def expect_sum(step, expected_diff):
    "Then I expect the difference to be <n>"
    assert step.context.difference == expected_diff, 'The expected difference {0} does not match actual difference {1}'.format(
        expected_diff. step.context.difference)


@given('I have an instable function')
def have_instable_function(step):
    "Given I have an instable function"
    pass


@when('I execute it')
def execute_instable_function(step):
    "When I execute it"
    pass


@then('I expect it to pass')
def expect_instable_function_pass(step):
    "Then I expect it to pass"
    pass


@given('I have the following heros')
def have_heros(step):
    "Given I have the following heros"
    step.context.heros = step.table


@when('I capitalize their first name')
def cap_first_name(step):
    "When I capitalize their first name"
    for hero in step.context.heros:
        hero['firstname'] = hero['firstname'].upper()


@then('I have the following names')
def have_names(step):
    "Then I have the following names"
    assert list(x['firstname'] for x in step.context.heros) == list(
            x['cap_heroname'] for x in step.table)


@given('I have the following quote')
def have_quote(step):
    "Given I have the following quote"
    step.context.quote = step.text


@when("I look for it's author")
def lookup_author(step):
    "When I look for it's author"
    step.context.author = 'Shakespeare'


@then('I will find {:S}')
def expect_author(step, author):
    "Then I will find <author>"
    assert step.context.author == author
