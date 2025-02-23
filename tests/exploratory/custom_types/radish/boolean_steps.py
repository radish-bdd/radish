from radish import then, when


@when("I have the value {:Boolean}")
def have_value(step, boolean):
    step.context.boolean = boolean


@then("I expect it to be parsed as True")
def expect_true(step):
    assert step.context.boolean is True


@then("I expect it to be parsed as False")
def expect_false(step):
    assert step.context.boolean is False
