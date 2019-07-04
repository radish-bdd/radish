Feature: Parse a Feature with a Scenario Outline
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Scenario Outline.

    Scenario Outline: A simple Scenario containing three Steps
        Given the webservice is started
        When the <route> route is queried
        Then the status code is <status-code>

    Examples:
        | route         | status-code |
        | /foo/bar      | 200         |
        | /non-existant | 404         |

