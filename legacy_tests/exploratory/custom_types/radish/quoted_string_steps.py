from radish import given, when, then


@given("I have the string {:QuotedString}")
def have_string(step, string):
    step.context.string = string


@when("I capitalize this string")
def capitalize_string(step):
    step.context.string = step.context.string.capitalize()


@then("I expect the string to be {:QuotedString}")
def expect_string(step, expected_string):
    assert step.context.string == expected_string, 'Expected "{0}" got "{1}"'.format(
        expected_string, step.context.string
    )
