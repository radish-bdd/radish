Feature: Parse a Feature with a Background and a Rule with a Scenario
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Background and a Rule with a Scenario.

    Background:
        Given the webservice is started

    Rule: all routes can be queried

        Scenario: A simple Scenario containing three Steps
            When the /foo/bar route is queried
            Then the status code is 200
