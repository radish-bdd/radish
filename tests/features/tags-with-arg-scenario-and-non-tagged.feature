@foo(bar)
Feature: Tag with Arguments
    Radish shall support Tags with Arguments.

    @sometag(somevalue) @othertag othervalue
    Scenario: Some Scenario
        Given I have a Step
        When I do something
        Then I expect something

    Scenario: Some Untagged Scenario
        Given I have a Step
        When I do something
        Then I expect something
