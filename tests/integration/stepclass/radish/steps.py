# -*- coding: utf-8 -*-

from radish import steps

@steps
class Calculator(object):
    def have_number(self, step, number):
        """I have the number {number:g}"""
        step.context.numbers.append(number)

    def sum_numbres(self, step):
        """I sum them"""
        step.context.result = sum(step.context.numbers)

    def expect_result(self, step, result):
        """I expect the result to be {result:g}"""
        assert step.context.result == result
