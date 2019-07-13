Feature: Ignore Scenario via Tag
    Radish shall support to ignore a
    Scenario via Tags

    @foo
    Scenario: Ignored Scenario
        Given I have a Step
        When I do something
        Then I expect something

    @bar
    Scenario: Parsed Scenario
        Given I have a Step
        When I do something
        Then I expect something

    Scenario: Another parsed Scenario
        Given I have a Step
        When I do something
        Then I expect something
