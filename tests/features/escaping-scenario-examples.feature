Feature: Escape PIPE in Example value
    Radish shall be able to detect escaped PIPEs
    in a Scenario Example value

    Scenario Outline: Regular Scenario
        I do some stuff <foo> <bar> <foobar>

    Examples:
        | foo | bar     | foobar |
        | 1   | hei\|ho | 2      |
        | 1   | hei\\ho | 2      |
