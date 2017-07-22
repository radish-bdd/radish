Feature: Background with subsequent tagged Scenario
    Radish shall support parsing Backgrounds with a
    subsequent parsed Scenario.

    Background: A simple Background
        Given I have the number 5
        And I have the number 3

    @foo
    @bar
    Scenario: Add numbers
        When I add them up
        Then I expect the sum to be 8
