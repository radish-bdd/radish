Feature: Hook Error Reporting
    In order to find issues in radish Hooks
    quickly, radish should give good error
    messages on failures.

    Scenario: Error Reporting on Exceptions raised during Hook calling
        Given the Feature File "error-reporting.feature"
            """
            Feature: Some Feature

                Scenario: Some Scenario
                    Given some Step
            """
        And the base dir module "steps.py"
            """
            from radish import given, before

            @before.each_feature()
            def before_each_feature(feature):
                raise RuntimeError("some runtime Error occurred")


            @given("some Step")
            def some_step(step):
                ...
            """
        When the "error-reporting.feature" is run
        Then the exit code should be 1
        And the output to match:
            """
            Feature: Some Feature
            1 Feature \(1 untested\)
            1 Scenario \(1 untested\)
            1 Step \(1 untested\)
            Run \d+ finished within [\d.]+ seconds

            An error occured while running the Feature Files:
            The '@before.each_feature' Hook 'before_each_feature' raised an RuntimeError: some runtime Error occurred
            """

    Scenario: Error Reporting on Exceptions raised during Module import
        Given the Feature File "error-reporting.feature"
            """
            Feature: Some Feature

                Scenario: Some Scenario
                    Given some Step
            """
        And the base dir module "steps.py"
            """
            from radish import given, before

            def some_func():
                raise RuntimeError("some runtime Error occurred")

            some_func()
            """
        When the "error-reporting.feature" is run
        Then the exit code should be 1
        And the output to match:
            """

            An error occured while loading modules from the basedirs:
            Unable to import module 'steps' from '(.*?)/steps.py': some runtime Error occurred
            """
