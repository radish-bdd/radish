Feature: Get User from database
    In order to test custom argument expression
    I'll do this simple example.

    Scenario: Get User from database
        Given I have the following heros in the database
            | forename | surname | hero      |
            | Peter    | Parker  | Spiderman |
            | Bruce    | Wayne   | Batman    |
        When I query for the hero with name Spiderman
        Then I expect it's name to be Peter Parker
