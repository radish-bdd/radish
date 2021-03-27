Feature: Support Scenario Parsing
    Radish should run only the selected Scenarios.

    Background: Add steps to pass a Scenario
        Given the base dir module "steps.py"
            """
            from radish import then

            @then("the Step passes")
            def pass_it(step):
                assert True
            """

    Scenario: Run all Scenarios
        Given the Feature File "ThreeScenario.feature"
            """
            Feature: Simple three Scenario feature

                Scenario: Scenario One
                    Then the Step passes

                Scenario: Scenario Two
                    Then the Step passes

                Scenario: Scenario Three
                    Then the Step passes
            """
        When the "ThreeScenario.feature" is run with the options "--no-ansi"
        Then the exit code should be 0
        And the output to match:
        """
        Feature: Simple three Scenario feature
            Scenario: Scenario One
                Then the Step passes
                Then the Step passes

            Scenario: Scenario Two
                Then the Step passes
                Then the Step passes

            Scenario: Scenario Three
                Then the Step passes
                Then the Step passes

        1 Feature \(1 passed\)
        3 Scenarios \(3 passed\)
        3 Steps \(3 passed\)
        """

    Scenario: Run only Scenario One
        Given the Feature File "ThreeScenario.feature"
            """
            Feature: Simple three Scenario feature

                Scenario: Scenario One
                    Then the Step passes

                Scenario: Scenario Two
                    Then the Step passes

                Scenario: Scenario Three
                    Then the Step passes
            """
        When the "ThreeScenario.feature" is run with the options "--no-ansi -s=1"
        Then the exit code should be 1
        And the output to match:
        """
        Feature: Simple three Scenario feature
            Scenario: Scenario One
                Then the Step passes
                Then the Step passes

        1 Feature \(1 untested\)
        3 Scenarios \(1 passed, 2 untested\)
        3 Steps \(1 passed, 2 untested\)
        """
    
    Scenario: Run only Scenario Two and Three
        Given the Feature File "ThreeScenario.feature"
            """
            Feature: Simple three Scenario feature

                Scenario: Scenario One
                    Then the Step passes

                Scenario: Scenario Two
                    Then the Step passes

                Scenario: Scenario Three
                    Then the Step passes
            """
        When the "ThreeScenario.feature" is run with the options "--no-ansi --scenarios 2,3"
        Then the exit code should be 1
        And the output to match:
        """
        Feature: Simple three Scenario feature
            Scenario: Scenario Two
                Then the Step passes
                Then the Step passes

            Scenario: Scenario Three
                Then the Step passes
                Then the Step passes

        1 Feature \(1 untested\)
        3 Scenarios \(1 untested, 2 passed\)
        3 Steps \(1 untested, 2 passed\)
        """
