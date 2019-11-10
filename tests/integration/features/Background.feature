Feature: Support a Feature Background
    In order to be Gherkin compatible
    radish supports the Background block
    in a Feature.

    Scenario: A Background is ran before a Scenario
        Given the Feature File "background.feature"
            """
            Feature: Some Feature

                Background:
                    Given the setup is done

                Scenario: a fancy Example
                    Then the setup has been done
            """
        And the base dir module "steps.py"
            """
            from radish import given, then

            @given("the setup is done")
            def do_setup(step):
                step.context.setup = True


            @then("the setup has been done")
            def expect_setup_done(step):
                assert step.context.setup
            """
        When the "background.feature" is run
        Then the exit code should be 0

    Scenario: The Scenario Hook is run before the Background Steps
        Given the Feature File "background.feature"
            """
            Feature: Some Feature

                Background:
                    Given the setup is done

                Scenario: a fancy Example
                    Then the setup has been done
            """
        And the base dir module "steps.py"
            """
            from radish import given, then, before

            @before.each_scenario()
            def before_scenario(scenario):
                scenario.context.setup = None


            @given("the setup is done")
            def do_setup(step):
                assert step.context.setup is None
                step.context.setup = True


            @then("the setup has been done")
            def expect_setup_done(step):
                assert step.context.setup
            """
        When the "background.feature" is run
        Then the exit code should be 0

    Scenario: Each Scenario has it's own copy of the Background
        Given the Feature File "background.feature"
            """
            Feature: Some Feature

                Background:
                    Given the setup is done

                Scenario: First Scenario
                    Then the setup has been done

                Scenario: Second Scenario
            """
        And the base dir module "steps.py"
            """
            from radish import given, then

            @given("the setup is done")
            def do_setup(step):
                assert not hasattr(step.context, "setup")
                step.context.setup = True


            @then("the setup has been done")
            def expect_setup_done(step):
                assert step.context.setup
            """
        When the "background.feature" is run
        Then the exit code should be 0
