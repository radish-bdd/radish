Feature: Feature with Scenario and ScenarioOutlines
    In order to demonstrate the ScenarioOutline
    feature I write this test

    Scenario: Add numbers
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7

    Scenario Outline: some fancy scenario
        Given I have the number <number>
        When I add <delta> to my number
        Then I expect the number to be <result>

    Examples:
        | number | delta | result |
        | 5      | 2     | 7      |
        | 10     | 3     | 13     |
        | 15     | 6     | 21     |

    Scenario: some other normal scenario
        Given I have the number 5
        When I add 11 to my number
        Then I expect the number to be 16
