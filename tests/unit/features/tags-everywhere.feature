@foo
@bar
Feature: Support Tags everywhere
    Radish shall support tags everywhere!

    @regular_scenario
    Scenario: Regular Scenario with Tags
        I do some stuff

    @scenario_outline
    Scenario Outline: Scenario Outline with Tags
        I do some stuff <foo>

    Examples:
        | foo |
        | bar |

    @scenario_loop
    Scenario Loop 2: Scenario Loop with Tags
        I do some stuff

