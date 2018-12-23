# -*- coding: utf-8 -*-

from radish import custom_type


@custom_type("is_plugged_in", r"(plugged in|not plugged in)")
def is_plugged_in(text):
    return text == "plugged in"


@custom_type("is_registered", r"(not )?to be registered")
def is_registered(text):
    return text == "to be registered"
