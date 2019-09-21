Feature: Test the radish Constants
    In order to simplify recurring constant
    values within a Feature File
    radish supports Constant Tags.

    Scenario: Feature and Scenario Constants
        Given the Feature File "constants.feature"
            """
            @constant(first_addend: 5)
            Feature: Constants

                @constant(second_addend: 2)
                Scenario: Adding numbers
                    When the numbers ${first_addend} and ${second_addend} are summed
                    Then the result is 7
            """
        And the base dir module "steps.py"
            """
            from radish import when, then

            @when("the numbers {:int} and {:int} are summed")
            def sum_up(step, first_addend, second_addend):
                step.context.addends = [first_addend, second_addend]
                step.context.sum = sum(step.context.addends)


            @then("the result is {:int}")
            def expect_result(step, result):
                assert step.context.sum == result
            """
        When the "constants.feature" is run with the options "--no-ansi --no-step-rewrites"
        Then the exit code should be 0
        And the output to match:
            """
            @constant\(first_addend: 5\)
            Feature: Constants
                @constant\(second_addend: 2\)
                Scenario: Adding numbers
                    When the numbers \$\{first_addend\} and \$\{second_addend\} are summed
                    Then the result is 7

            1 Feature \(1 passed\)
            1 Scenario \(1 passed\)
            2 Steps \(2 passed\)
            """
