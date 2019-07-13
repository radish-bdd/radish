Feature: Restricted site support
    As a user of AwesomeSite
    I want to restrict my personal sites
    to specific users.

    @precondition(precondition-level-0.feature: Have a multi user setup)
    Scenario: Grant access to personal site
        Given Bruce grants access to Tony
        When I'm logged in as Tony
        Then I can access Bruce personal site
