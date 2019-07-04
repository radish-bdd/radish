Feature: Parse a Feature with multiple Rules with a Scenario
    The radish parser should be able to
    parse a Feature File containing a Feature
    with multiple Rules with a Scenario.

    Background:
        Given the webservice is started


    Rule: all routes can be queried

        Scenario: A simple Scenario containing three Steps
            When the /foo/bar route is queried
            Then the status code is 200

    Rule: the insert routes can be POSTed

        Scenario: A simple Scenario containing three Steps
            When the /foo/create route is POSTed
            Then the status code is 201
