Feature: Support Scenario Loop
    Radish shall support Scenario Loops.

    Scenario Loop: This is a looped Scenario
        Given I have an instable function
        When I execute it
        Then I expect it to pass

    Iterations: 3
