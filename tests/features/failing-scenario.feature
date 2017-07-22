Feature: Add some numbers

    Scenario: Add some numbers
        Given I have the number 1
        And I have the number 2
        When I add them up
        Then I expect the sum to be 42
