Feature: Parse a Feature with a Scenario with Steps including data tables with escaped VBARs
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Scenario which has some Steps
    using data tables having escaped VBARs.

    Scenario: A Scenario containing three Steps and data tables
        Given the webservice is started
        When the following routes are queried
            | host1.com\|foo | /foo/bar      |
            | host2.com      | /foo/bar\|bla |
        Then the status codes are
            | 200\|201 |
            | 404\|405 |
