Feature: Parse a Feature with a Background and Scenario Outline
    The radish parser should be able to
    parse a Feature File containing a Feature
    with a Background and a Scenario Outline.

    Background:
        Given the webservice is started

    Scenario Outline: A simple Scenario containing three Steps
        When the <route> route is queried
        Then the status code is <status-code>

    Examples:
        | route         | status-code |
        | /foo/bar      | 200         |
        | /non-existant | 404         |

