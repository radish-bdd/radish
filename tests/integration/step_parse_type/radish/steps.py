# -*- coding: utf-8 -*-

from radish import given, when, then


@given('I have the numbers {numbers:Number+}')
def have_number(step, numbers):
    step.context.numbers.extend(numbers)


@given('I have the following numbers {numbers:NumberList}')
def have_number(step, numbers):
    step.context.numbers.extend(numbers)


@when('I sum them')
def sum_numbers(step):
    step.context.result = sum(step.context.numbers)


@then('I expect the result to be {result:g}')
def expect_result(step, result):
    assert step.context.result == result


@given('I have studied the questions')
def studied_questions(step):
    pass


@when('I have to answer it')
def answer_question(step):
    pass


@then('I say "{answer:AnswerChoice}"')
def say_answer(step, answer):
    assert answer == 'yes'
