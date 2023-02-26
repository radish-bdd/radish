@author(mario) @date(Sat, 25 Feb 2023 19:53:53 +0100)
Feature: Support Multiple Tags in a single line
    Radish shall support multiple tags in a single line (even with value)!

    @with_out_value @author(luigi)
    Scenario: Regular Scenario with Tags
        Given I have a Step
        When I do something
        Then I expect something
