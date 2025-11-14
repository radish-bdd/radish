from radish.stepregistry import given, step, then, when
from radish.terrain import pick, world


@step("I don't have a pick decorated method")
def dont_have_pick_method(step):
    if hasattr(world, "pick_decorated"):
        delattr(world, "pick_decorated")


@given("I have a method decorated with pick")
def add_pick_step(step):
    @pick
    def pick_decorated():
        return 42

    step.context.decorate_method_name = pick_decorated.__name__


@then("I expect the pick step to be in the world")
def expect_pick_step(step):
    assert hasattr(world, "pick_decorated"), "World is missing the decorated method pick_decorated"


@then("I expect the pick step not to be in the world")
def expect_pick_step_missing(step):
    assert not hasattr(world, "pick_decorated"), "World has the decorated method pick_decorated"


@when("I call the pick decorated method")
def call_pick_decorated_method(step):
    step.context.pick_result = world.pick_decorated()


@then("I expect the pick result to be {expected_result:d}")
def expect_pick_result(step, expected_result):
    assert step.context.pick_result == expected_result, (
        f"Expected pick result to be {expected_result} but was {step.context.pick_result}"
    )
