Feature: Add some numbers

    Scenario Outline: Add some numbers
        Given I have the number <x>
        And I have the number <y>
        When I add them up
        Then I expect the sum to be <z>

    Examples:
        | x | y | z  |
        | 1 | 2 | 3  |
        | 4 | 5 | 42 |
