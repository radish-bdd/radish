.. _bdd_xml_output:

##############
BDD XML Output
##############

Radish can BDD XML output using ``--bdb-xml``. The format of the XML as is
as follows:

**XML declaration**

.. code:: xml

  <?xml version='1.0' encoding='utf-8'?>

**<testrun>** is a top level tag

:agent:
  Agent of the test run composed of the user and hostname of the machine.
  Format: user@hostname
:duration:
  Duration of test run in seconds rounded to the 10 decimal points.
:starttime:
  Start time of the testrun run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS
:endtime:
  End time of the testrun run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS

example:

.. code:: xml

  <testrun>
    agent="user@computer"
    duration="0.0005660000"
    starttime="2017-02-18T07:06:55">
    endtime="2017-02-18T07:06:56"
  >

The **<testrun>** contains the following tags

**<feature>** tag

:id:
  Test run index id of the Feature. First feature to run is 1, second is 2 and
  so on.
:sentence:
  Feature sentence.
:result:
  Run state result of Feature run as described in
  :ref:`quickstare#run_state_result`
:testfile:
  Path to the file name containing the feature. The path is relative to
  the ``basedir``.
:duration:
  Duration of Feature run in seconds rounded to the 10 decimal points.
:starttime:
  Start time of the Feature run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS
:endtime:
  End time of the Feature run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS

example:

.. code:: xml

    <feature
      id="1"
      sentence="Step Parameters (tutorial03)"
      result="failed"
      testfile="./example.feature"
      duration="0.0008730000"
      starttime="2017-02-18T07:06:55"
      endtime="2017-02-18T07:06:55"
    >

The **<feature>** tag contains the following tags:

**<description>** tag:

:tag content: CDATA enclosed description of the feature.

.. code:: xml

  <description>
    <![CDATA[This feature test following functionality
    - awesomeness
    - more awesomeness
    ]]>
  </description>

**<scenarios>** tag:

Contains list of **<screnario>** tags

example:

.. code:: xml

  <scenarios>

The **<scenarios>** tag contains the following tags:

**<scenario>** tag:

:id:
  Test run index id of the Scenario. First scenario to run is 1, second is 2
  and so on.
:sentence:
  Scenario sentence.
:result:
  Run state result of Scenario run as described in
  :ref:`quickstare#run_state_result`
:testfile:
  Path to the file name containing the Scenario. The path is relative to
  the ``basedir``.
:duration:
  Duration of Scenario run in seconds rounded to the 10 decimal points.
:starttime:
  Start time of the Scenario run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS
:endtime:
  End time of the Scenario run.
  Combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS

example:

.. code:: xml

  <scenario
    id="1"
    sentence="Blenders"
    result="failed"
    testfile="./example.feature"
    duration="0.0007430000"
    endtime="2017-02-18T07:06:55"
    starttime="2017-02-18T07:06:55"
  >

The **<scenario>** tag contains the following tags:

**<step>** tag:

:id:
  Test run index id of the Step. First Step to run is 1, second is 2
  and so on.
:sentence:
  Step sentence.
:result:
  Run state result of Step run as described in
  :ref:`quickstare#run_state_result`
:testfile:
  Path to the file name containing the Step. The path is relative to
  the ``basedir``.
:duration:
  Duration of Step run in seconds rounded to the 10 decimal points.
:starttime:
  Start time of the Step run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS
:endtime:
  End time of the Step run.
  Format: combined date and time representations, where date and time is separated by
  letter "T". Format: YYYY-MM-DDTHH:MM:SS


example:

.. code:: xml

  <step
    id="1"
    sentence="Given I put &quot;apples&quot; in a blender"
    result="passed"
    testfile="./example.feature"
    duration="0.0007430000"
    endtime="2017-02-18T07:06:55"
    starttime="2017-02-18T07:06:55"
  >

The **<step>** MAY tag contains the following tags if error has occured:

**<failure>** tag:

:message:
  Test run index id of the Step. First Step to run is 1, second is 2
  and so on.
:type:
  Step sentence.
:tag content:
  CDATA enclosed failure reason specifically excepion traceback.


example:

.. code:: xml

  <failure
    message="hello"
    type="Exception">
      <![CDATA[Traceback (most recent call last):
        File "/tmp/bdd/_env36/lib/python3.6/site-packages/radish/stepmodel.py", line 91, in run
          self.definition_func(self, *self.arguments)  # pylint: disable=not-callable
        File "/tmp/bdd/radish/radish/example.py", line 34, in step_when_switch_blender_on
          raise Exception("show off radish error handling")
      Exception: show off radish error handling
     ]]>
  </failure>
