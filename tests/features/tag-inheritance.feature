@some_feature
Feature: Support Tag Inheritance
    Radish shall support Tag inheritance

    @good_case
    Scenario: Some good case Scenario test
        Given I have a Step
        When I do something
        Then I expect something

    @bad_case
    Scenario: Some bad case Scenario test
        Given I have a Step
        When I do something
        Then I expect something

    @good_case
    Scenario: Some other good case Scenario test
        Given I have a Step
        When I do something
        Then I expect something
