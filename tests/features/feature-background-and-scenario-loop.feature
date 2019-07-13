Feature: Parse a Feature with a Background and Scenario Loop
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Background and a Scenario Loop.

    Background:
        Given the webservice is started

    Scenario Loop: A simple Scenario containing three Steps
        When the <route> route is queried
        Then the status code is <status-code>

    Iterations: 2
