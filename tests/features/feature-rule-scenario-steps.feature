Feature: Feature with a Scenario and Steps
    Radish shall support parsing a Feature containing
    a Scenario which contains multiple Steps

    Background: some background
        Given I do a setup

    Scenario: Scenario with multiple Steps
        Given I have a Step
        When I do something
        Then I expect something

    Rule: some ruuuule

        Example: Scenario with multiple Steps
            Given I have a Step
            When I do something
            Then I expect something

    Rule: some other ruuuule

        Example Outline: Scenario with multiple Steps
            Given I have a Step
            When I do something
            Then I expect something

        Examples:
            | foo |
            | bar |

        Scenario: Scenario with multiple Steps
            Given I have a Step
            When I do something
            Then I expect something
