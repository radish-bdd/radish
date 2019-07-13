Feature: Setup database
    In order to support the automatic setup of
    the database and test these features.

    Scenario: Setup database and insert default values
        Given I install the database server
        When I add all default users
        And I add all default types
        And I initialize the database error handlers
        And I set the permissions for the administrator tables
        And I index imported fields
        Then I expect my installation to be complete
