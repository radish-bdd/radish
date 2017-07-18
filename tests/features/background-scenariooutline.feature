Feature: Background for Scenario Outline
    Radish shall support Backgrounds for
    Scenario Outlines.
    The Background shall be assigned to
    each Example Scenario.

    Background: A simple Background
        Given I have the number 5
        And I have the number 3

    Scenario Outline: Add numbers
        When I <operator> them up
        Then I expect the sum to be <result>

    Examples:
        | operator | result |
        | add      | 8      |
        | subtract | 2      |
