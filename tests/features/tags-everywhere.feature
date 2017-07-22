@foo
@bar
Feature: Support Tags everywhere
    Radish shall support tags everywhere!

    @regular_scenario
    Scenario: Regular Scenario with Tags
        Given I have a Step
        When I do something
        Then I expect something


    @scenario_outline
    Scenario Outline: A Scenario Outline
        Given I have the number <x>
        And I have the number <y>
        When I add them up
        Then I expect the sum to be <z>

    Examples:
        | x | y | z |
        | 1 | 2 | 3 |
        | 4 | 5 | 9 |

    @scenario_loop
    Scenario Loop 2: Scenario Loop with Tags
        Given I have a Step
        When I do something
        Then I expect something
