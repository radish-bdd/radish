Feature: Supprt Junit XML Format
    In order to report radish test runs
    radish shall support to generate
    correct Junit XML files.

    Background: Add steps to pass and fail a Scenario
        Given the base dir module "steps.py"
            """
            from radish import then

            @then("the Step passes")
            def pass_it(step):
                assert True


            @then("the Step fails")
            def fail_it(step):
                assert False, "Some Failure occurred"


            @then("the Step skips")
            def skip_it(step):
                step.skip()
            """

    Scenario: Report empty Feature File Run
        Given the Feature File "empty.feature"
            """
            Feature: Empty
                Some empty Feature
            """
        When the "empty.feature" is run with the options "--junit-xml {ctx_dir}/results.xml"
        Then the exit code should be 0
        And the XML file results.xml validates against junit.xsd
        And the XML file results.xml has the value "radish" at "/testsuites/@name"

    Scenario: Report a single passed Scenario as Testcase
        Given the Feature File "single-passed.feature"
            """
            Feature: Single Passed
                Single passed Scenario

                Scenario: Pass
                    Then the Step passes
            """
        When the "single-passed.feature" is run with the options "--junit-xml {ctx_dir}/results.xml"
        Then the exit code should be 0
        And the XML file results.xml validates against junit.xsd
        And the XML file results.xml has the content:
            """
            <\?xml version='1.0' encoding='utf-8'\?>
            <testsuites name="radish" time="[0-9.]{5}">
              <testsuite name="Single Passed" tests="1" skipped="0" failures="0" errors="0" time="[0-9.]{5}">
                <testcase classname="Single Passed" name="Pass" time="[0-9.]{5}"/>
              </testsuite>
            </testsuites>
            """

    Scenario: Report multiple passed Scenarios as Testcases
        Given the Feature File "multiple-passed.feature"
            """
            Feature: Multiple Passed
                Multiple passed Scenario

                Scenario: Pass 1
                    Then the Step passes

                Scenario: Pass 2
                    Then the Step passes
            """
        When the "multiple-passed.feature" is run with the options "--junit-xml {ctx_dir}/results.xml"
        Then the exit code should be 0
        And the XML file results.xml validates against junit.xsd
        And the XML file results.xml has the content:
            """
            <\?xml version='1.0' encoding='utf-8'\?>
            <testsuites name="radish" time="[0-9.]{5}">
              <testsuite name="Multiple Passed" tests="2" skipped="0" failures="0" errors="0" time="[0-9.]{5}">
                <testcase classname="Multiple Passed" name="Pass 1" time="[0-9.]{5}"/>
                <testcase classname="Multiple Passed" name="Pass 2" time="[0-9.]{5}"/>
              </testsuite>
            </testsuites>
            """

    Scenario: Report a single skipped Scenario as Testcase
        Given the Feature File "single-skipped.feature"
            """
            Feature: Single Skipped
                Single skipped Scenario

                Scenario: Skip
                    Then the Step skips
            """
        When the "single-skipped.feature" is run with the options "--junit-xml {ctx_dir}/results.xml"
        Then the exit code should be 1
        And the XML file results.xml validates against junit.xsd
        And the XML file results.xml has the content:
            """
            <\?xml version='1.0' encoding='utf-8'\?>
            <testsuites name="radish" time="[0-9.]{5}">
              <testsuite name="Single Skipped" tests="1" skipped="1" failures="0" errors="0" time="[0-9.]{5}">
                <testcase classname="Single Skipped" name="Skip" time="[0-9.]{5}">
                  <skipped/>
                </testcase>
              </testsuite>
            </testsuites>
            """

    Scenario: Report single failed Scenario as Testcases
        Given the Feature File "single-failed.feature"
            """
            Feature: Single Failed
                Single failed Scenario

                Scenario: Failed
                    Then the Step fails
            """
        When the "single-failed.feature" is run with the options "--junit-xml {ctx_dir}/results.xml"
        Then the exit code should be 1
        And the XML file results.xml validates against junit.xsd
        And the XML file results.xml has the content:
            """
            <\?xml version='1.0' encoding='utf-8'\?>
            <testsuites name="radish" time="[0-9.]{5}">
              <testsuite name="Single Failed" tests="1" skipped="0" failures="1" errors="0" time="[0-9.]{5}">
                <testcase classname="Single Failed" name="Failed" time="[0-9.]{5}">
                  <failure type="AssertionError" message="Then the Step fails"><!\[CDATA\[Then the Step fails

            Traceback \(most recent call last\):
              File "(.*?)step.py", line [0-9]+, in run
                self.step_impl.func\(self, \*args\)
              File "(.*?)steps.py", line [0-9]+, in fail_it
                assert False, "Some Failure occurred"
            AssertionError: Some Failure occurred
            \]\]></failure>
                </testcase>
              </testsuite>
            </testsuites>
            """

    Scenario: Report passed and failed Scenarios as Testcases
        Given the Feature File "passed-failed.feature"
            """
            Feature: Passed and Failed
                Passed and Failed Scenario

                Scenario: Passed
                    Then the Step passes

                Scenario: Failed
                    Then the Step fails
            """
        When the "passed-failed.feature" is run with the options "--junit-xml {ctx_dir}/results.xml"
        Then the exit code should be 1
        And the XML file results.xml validates against junit.xsd
        And the XML file results.xml has the content:
            """
            <\?xml version='1.0' encoding='utf-8'\?>
            <testsuites name="radish" time="[0-9.]{5}">
              <testsuite name="Passed and Failed" tests="2" skipped="0" failures="1" errors="0" time="[0-9.]{5}">
                <testcase classname="Passed and Failed" name="Passed" time="[0-9.]{5}"/>
                <testcase classname="Passed and Failed" name="Failed" time="[0-9.]{5}">
                  <failure type="AssertionError" message="Then the Step fails"><!\[CDATA\[Then the Step fails

            Traceback \(most recent call last\):
              File "(.*?)step.py", line [0-9]+, in run
                self.step_impl.func\(self, \*args\)
              File "(.*?)steps.py", line [0-9]+, in fail_it
                assert False, "Some Failure occurred"
            AssertionError: Some Failure occurred
            \]\]></failure>
                </testcase>
              </testsuite>
            </testsuites>
            """
