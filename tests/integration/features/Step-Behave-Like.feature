Feature: Test the radish Step behave-like Feature
    In order to call another Step from
    within a Step Implementation Function radish
    provides the behave-like Feature.

    Scenario: Call another Step with the behave-like Feature
        Given the Feature File "behave-like.feature"
            """
            Feature: Behave-Like

                Scenario: Behave-Like
                    When something is run
                    Then another thing was run, too
            """
        And the base dir module "steps.py"
            """
            from radish import when, then

            @when("something is run")
            def something_run(step):
                step.context.something = True
                step.behave_like("When another thing is run")


            @when("another thing is run")
            def anotherthing_run(step):
                step.context.another_thing = True


            @then("another thing was run")
            def expect_anotherthing_ran(step):
                assert step.context.something
                assert step.context.another_thing
            """
        When the "behave-like.feature" is run
        Then the exit code should be 0

    Scenario: Call two other Steps with the behave-like Feature
        Given the Feature File "behave-like.feature"
            """
            Feature: Behave-Like

                Scenario: Behave-Like
                    When something is run
                    Then the counter is 2
            """
        And the base dir module "steps.py"
            """
            from radish import before, when, then

            @before.each_scenario()
            def setup_counter(scenario):
                scenario.context.counter = 0

            @when("something is run")
            def something_run(step):
                step.behave_like("When the counter is increased")
                step.behave_like("When the counter is increased")


            @when("the counter is increased")
            def increase_counter(step):
                step.context.counter += 1


            @then("the counter is {:int}")
            def expect_counter(step, counter):
                assert step.context.counter == counter
            """
        When the "behave-like.feature" is run
        Then the exit code should be 0

    Scenario: Detect behave-like Call Recursions
        Given the Feature File "behave-like.feature"
            """
            Feature: Behave-Like

                Scenario: Behave-Like
                    When something is run
            """
        And the base dir module "steps.py"
            """
            from radish import when, then

            @when("something is run")
            def something_run(step):
                step.behave_like("When something is run")
            """
        When the "behave-like.feature" is run
        Then the run should fail with a StepBehaveLikeRecursionError
            """
            Detected a infinit recursion in your ``step.behave_like`` calls
            """
