Feature: Unknown Scenario Precondition Dependency
    Radish shall detect when Scenario Precondition
    Dependency cannot be found.

    @precondition(precondition-unknown-scenario-same-feature.feature: Unknown Scenario)
    Scenario: Some scenario
        I do some stuff
