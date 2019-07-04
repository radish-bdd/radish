Feature: Parse a Feature with a Scenario with Tags
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Scenario with some Tags

    @tag-a
    @tag-b
    Scenario: A simple Scenario containing three Steps
        Given the webservice is started
        When the /foo/bar route is queried
        Then the status code is 200

