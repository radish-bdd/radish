Feature: Test behave-like feature
    In order to demonstrate the behave-like
    feature I write this test

    Scenario: Check calculator
        Given I setup the database
        When I add the users
            | Timo     | Furrer  | tuxtimo@gmail.com |
        Then I expect the user "Timo Furrer" in the database
