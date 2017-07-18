Feature: Restricted site support
    As a user of AwesomeSite
    I want to restrict my personal sites
    to specific users.

    Background: Have a multi user setup
        Given a user named Bruce
        And a user named Peter
        And a user named Tony
        And a user named Sheldon
        And a user named Leonard
        And a personal site owned by Bruce
        And a personal site owned by Leonard

    Scenario Outline: Grant access to personal site
        Given <producer> grants access to <consumer>
        When I'm logged in as <consumer>
        Then I can access <producer> personal site

    Examples:
        | producer | consumer |
        | Bruce    | Tony     |
        | Leonard  | Sheldon  |
