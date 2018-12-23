@everything
Feature: Everything in one Feature
    A feature file with everything in it.

    Background: A simple Background
        Given I have the number 5
        And I have the number 3

    @foo
    Scenario: Add numbers
        When I add them up
        Then I expect the sum to be 8

    Scenario: Subtract numbers
        When I subtract them
        Then I expect the difference to be 2

    @bad
    Scenario: Subtract numbers wrongly
        When I subtract them
        Then I expect the difference to be 3

    Scenario Outline: A Scenario Outline
        Given I have the number <x>
        And I have the number <y>
        When I add them up
        Then I expect the sum to be <z>

    Examples:
        | x | y | z |
        | 1 | 2 | 3 |
        | 4 | 5 | 9 |

    Scenario Loop 2: This is a looped Scenario
        Given I have an instable function
        When I execute it
        Then I expect it to pass
