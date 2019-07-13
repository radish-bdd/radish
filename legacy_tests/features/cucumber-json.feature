@feature_tag
Feature: Cucumber json report generation

    @scenario_tag
    Scenario: Middle step failure - skipped step on the end
        Given I have the number 1
        And I have the number 2
        When I add them up with failure
        Then I expect the sum to be 42

    Scenario: Generate cucumber json report in middle of scenario execution
        When generate cucumber report
        Then genreated cucumber json equals to "cucumber-json.json"
