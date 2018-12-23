# -*- coding: utf-8 -*-

from radish import given, when, then


@given("the device is {is_plugged_in:is_plugged_in}")
def device_plugged_in(step, is_plugged_in):
    step.context.powered = False
    step.context.device_plugged_in = is_plugged_in


@when("I turn on the board")
def turn_on_board(step):
    step.context.powered = True


@then("I expect the device {is_registered:is_registered}")
def device_registered(step, is_registered):
    assert (
        step.context.powered
    ), "Board is not powered, thus device cannot be registered"
    # device is always registered when the device is plugged in
    assert step.context.device_plugged_in == is_registered, "Device is not regsitered"
