Feature: Parse a Feature with a Scenario with Steps including data tables
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Scenario which has some Steps
    using data tables.

    Scenario: A Scenario containing three Steps and data tables
        Given the webservice is started
        When the following routes are queried
            | host1.com | /foo/bar |
            | host2.com | /foo/bar |
        Then the status codes are
            | 200 |
            | 404 |
