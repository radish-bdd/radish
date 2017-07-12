Feature: Ignore Scenario via Tag
    Radish shall support to ignore a
    Scenario via Tags

    @foo
    Scenario: Ignored Scenario
        I do some stuff

    @bar
    Scenario: Parsed Scenario
        I do some stuff

    Scenario: Another parsed Scenario
        I do some stuff
