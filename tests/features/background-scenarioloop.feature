Feature: Background for Scenario Loop
    Radish shall support Backgrounds for
    Scenario Loops.
    The Background shall be assigned to
    each Iteration Scenario.

    Background: A simple Background
        Given I have the number 5
        And I have the number 3

    Scenario Loop 2: Add numbers
        When I add them up
        Then I expect the sum to be 8
