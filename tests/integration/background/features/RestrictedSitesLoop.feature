Feature: Restricted site support
    As a user of AwesomeSite
    I want to restrict my personal sites
    to specific users.

    Background: Have a multi user setup
        Given a user named Bruce
        And a user named Peter
        And a user named Tony
        And a personal site owned by Bruce

    Scenario Loop 2: Grant access to personal site
        Given Bruce grants access to Tony
        When I'm logged in as Tony
        Then I can access Bruce personal site
