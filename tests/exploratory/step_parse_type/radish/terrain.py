from radish import TypeBuilder, before, custom_type, register_custom_type


@before.each_scenario
def init_numbers(scenario):
    scenario.context.numbers = []


@custom_type("Number", r"\d+")
def number_type(text):
    """
    Return the text as number
    """
    return int(text)


# create cardinalty
register_custom_type(NumberList=TypeBuilder.with_many(number_type, listsep="and"))

# choice
register_custom_type(AnswerChoice=TypeBuilder.make_choice(["yes", "no"]))
