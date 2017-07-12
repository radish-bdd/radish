Feature: Simple Background
    Radish shall support simple Scenario
    Backgrounds.
    The Background shall be assigned to
    each Scenario.

    Background: A simple Background
        Given I have the number 5
        And I have the number 3

    Scenario: Add numbers
        When I add them up
        Then I expect the sum to be 8

    Scenario: Subtract numbers
        When I subtract them
        Then I expect the difference to be 2
