Feature: Support Generator Hooks
    In order to use Hooks as efficient
    as possbile radish should provide
    Generator Hooks.

    Scenario: A simple Generator Hook with before and after parts
        Given the Feature File "generator-hooks.feature"
            """
            Feature: Some Feature

                Scenario: Some Scenario
                    When there is a Step
            """
        And the base dir module "steps.py"
            """
            from radish import when, each_scenario, after


            @each_scenario(order=50)
            def for_each_scenario(scenario):
                scenario.context.number = 1
                yield
                scenario.context.number += 1

            @after.each_scenario(order=100)
            def assert_number(scenario):
                assert scenario.context.number == 2, (
                    "number should have been 2 but was {}".format(
                        scenario.context.number
                    )
                )

            @when("there is a Step")
            def some_step(step):
                pass
            """
        When the "generator-hooks.feature" is run
        Then the exit code should be 0

    Scenario: A simple Generator Hook used in multiple Scenarios
        Given the Feature File "generator-hooks.feature"
            """
            Feature: Some Feature

                Scenario: Some Scenario
                    When there is a Step

                Scenario: Some other Scenario
                    When there is a Step
            """
        And the base dir module "steps.py"
            """
            from radish import when, each_scenario, after


            @each_scenario(order=50)
            def for_each_scenario(scenario):
                scenario.context.number = 1
                yield
                scenario.context.number += 1

            @after.each_scenario(order=100)
            def assert_number(scenario):
                assert scenario.context.number == 2, (
                    "number should have been 2 but was {}".format(
                        scenario.context.number
                    )
                )

            @when("there is a Step")
            def some_step(step):
                pass
            """
        When the "generator-hooks.feature" is run
        Then the exit code should be 0
