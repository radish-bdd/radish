Feature: Parse a Feature with a Scenario Loop with Tags
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Scenario Loop with Tags.

    @tag-a
    @tag-b
    Scenario Loop: A simple Scenario containing three Steps
        Given the webservice is started
        When the <route> route is queried
        Then the status code is <status-code>

    Iterations: 2
