Feature: Match basic strings
    I want to be able to match custom strings
    which evaluate to True or False

    Scenario: Device is registered
        Given the device is plugged in
        When I turn on the board
        Then I expect the device to be registered

    Scenario: Device is not registered
        Given the device is not plugged in
        When I turn on the board
        Then I expect the device not to be registered
