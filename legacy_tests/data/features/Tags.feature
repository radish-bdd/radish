@good_case
Feature: some feature
    In order to test feature tags
    I write this feature

    @test_tags
    @good_case_scenario
    Scenario: Some tests
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7

    @test_tags
    Scenario: Some other tests 1
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7

    Scenario: Some other tests 2
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7

    @good_case_scenario
    Scenario: Some other tests 3
        Given I have the number 5
        When I add 2 to my number
        Then I expect the number to be 7
