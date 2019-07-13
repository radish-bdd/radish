Feature: Feature with Scenario and ScenarioLoop
    In order to demonstrate the ScenarioLoop
    feature I write this test

    Scenario: Add numbers
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7

    Scenario Loop 10: some fancy scenario
        Given I have the number 5
        When I add 12 to my number
        Then I expect the number to be 17

    Scenario: Add again numbers
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7
