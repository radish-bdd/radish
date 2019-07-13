Feature: Parse a Feature with a Scenario with Steps

    Scenario: A simple Scenario containing three Steps
        Given the webservice is started
        When the /foo/bar route is queried
        Then the status code is 200
