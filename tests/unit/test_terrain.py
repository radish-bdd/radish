from radish.terrain import pick, world


def test_pick_decorator_adds_function_to_world():
    """Test that the pick decorator adds the function to the world object."""
    assert not hasattr(world, "sample_function")

    @pick
    def sample_function():
        return "test"

    assert hasattr(world, "sample_function")
    assert world.sample_function() == "test"

    @pick
    def another_function(x, y=0):
        return x + y

    assert hasattr(world, "another_function")
    assert world.another_function(2, y=3) == 5, "Parameters not passed correctly."

    def func():
        return "overridden"

    func.__name__ = "sample_function"

    pick(func)

    assert world.sample_function() == "overridden", "The function was not overridden correctly."
