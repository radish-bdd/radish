Feature: Restricted site support
    As a user of AwesomeSite
    I want to restrict my personal sites
    to specific users.

    Background: Have a multi user setup
        Given a user named Bruce
        And a user named Peter
        And a user named Tony
        And a personal site owned by Bruce

    @precondition(RestrictedSites.feature: Grant access to personal site)
    Scenario: Do some more stuff
        Given a personal site owned by Tony
        When I'm logged in as Bruce
        Then I cannot access Tony personal site
