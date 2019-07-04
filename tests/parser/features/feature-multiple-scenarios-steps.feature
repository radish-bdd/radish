Feature: Parse a Feature with multiple Scenarios with Steps
    The radish parser should be able to
    parse a Feature File containing a Feature
    with multiple Scenarios which have some Steps.

    Scenario: A simple Scenario containing three Steps
        Given the webservice is started
        When the /foo/bar route is queried
        Then the status code is 200

    Scenario: Another simple Scenario containing three Steps
        Given the webservice is started
        When the /foo/not-existent route is queried
        Then the status code is 404
