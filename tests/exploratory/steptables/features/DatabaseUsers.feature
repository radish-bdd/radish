Feature: Test adding user to database
  In order to test the step table
  features of radish I test to add
  users to the database.

  Scenario: Add users to the database
    Given I have the following users
      | forename | surname | hero      |
      | Peter    | Parker  | Spiderman |
      | Bruce    | Wayne   | Batman    |
    When I add them to the database
    Then I expect 2 users in the database
