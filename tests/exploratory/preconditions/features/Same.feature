@foo
Feature: Support Precondition from same feature
    I want to be able to use a Scenario as precondition
    for a Scenario within the same Feature.

    Scenario: Precondition
        Given a user named Bruce
        And a user named Peter
        And a user named Tony
        And a personal site owned by Bruce

    @bar
    @precondition(Same.feature: Precondition)
    Scenario: Grant access to personal site
        Given Bruce grants access to Tony
        When I'm logged in as Tony
        Then I can access Bruce personal site
