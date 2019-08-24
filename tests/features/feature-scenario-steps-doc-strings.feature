Feature: Parse a Feature with a Scenario with Steps including doc strings
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Scenario which has some Steps
    using doc strings.

    Scenario: A Scenario containing three Steps and doc strings
        Given the webservice is started
        When the /foo/bar route is queried with the following body
            """
            {
              "foo": "Bar",
              "Bar": "foo"
            }
            """
        Then the status code is 200
