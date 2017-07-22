# -*- coding: utf-8 -*-

from radish import then


@then("I expect the result to be {result:g}")
def expect_result(step, result):
    assert step.context.result == result
