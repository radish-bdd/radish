Feature: Detect Scenario Precondition Recursion
    Radish shall detect a Scenario
    Precondition Recursion

    @precondition(precondition-recursion-helper.feature: Recursion)
    Scenario: Recursion
        I do some stuff
