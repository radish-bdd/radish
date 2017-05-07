Feature: Restricted site support
    As a user of AwesomeSite
    I want to restrict my personal sites
    to specific users.

    @precondition(Base.feature: Grant access to personal site)
    Scenario: Deny access to personal site
        Given Bruce grants access to Tony
        When I'm logged in as Peter
        Then I cannot access Bruce personal site
