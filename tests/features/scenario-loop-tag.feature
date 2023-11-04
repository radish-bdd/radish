Feature: Support Scenario Loop
    Radish shall support Scenario Loops.

    @arbitrary_tag
    Scenario Loop 2: This is a looped Scenario
        Given I have an instable function
        When I execute it
        Then I expect it to pass
