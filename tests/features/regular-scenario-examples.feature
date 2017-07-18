Feature: Detect Example usage error
    Radish shall detect if an attempt
    is made to use Examples with a
    regular Scenario.

    Scenario: Regular Scenario
        I do some stuff

    Examples:
            | foo |
            | 1   |
