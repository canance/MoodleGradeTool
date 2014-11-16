.. Substitutions

.. |Tester| replace:: :py:class:`~moodlegradetool.testing.Tester`

.. |Testers| replace:: :py:class:`Testers<moodlegradetool.testing.Tester>`

.. |parse| replace:: :py:meth:`~moodlegradetool.testing.Tester.parse_config`

.. |handles| replace:: :py:meth:`~moodlegradetool.testing.Tester.handlesconfig`

.. |start| replace:: :py:meth:`~moodlegradetool.testing.Tester.start`

=====================
Understanding Testers
=====================

Of all the classes in the MoodleGradeTool, |Testers| are probably the most complex. At first glance they are deceptively
simple, you only need to implement three methods to make one, but understanding how they interact with the everything
else is another matter.

In the :py:mod:`~moodlegradetool.testing` there are two lists :py:data:`~moodlegradetool.testing.testers`
and :py:data:`~moodlegradetool.testing.tests`. They hold the registered |Testers| and *Tests* respectively. Tests are
made from testers and configuration files ('.test' files).

.test files are searched for in the configuration folder selected earlier and are passed to registered |Testers| in
sequence. The first one that claims to handle that particular file will have its |parse| method called with the filename.
The code for this resides in the :py:meth:`~moodlegradetool.testing.findtests` method. |parse| will parse the file
and return a dictionary. That dictionary is then used to make a *Test* class that is a subclass of that tester. The
resulting *Test* is then added to the list of available tests.

Another way to think about it is that a |Tester| is the *Test* class's implementation and its configuration file is its
data. The two halves make one full *Test* class.


Making a tester
+++++++++++++++

To make your own |Tester| you need to need to start by implementing |parse|, |handles|, and |start| in a subclass
of |Tester|. After your class declaration be sure to call :py:meth:`~moodlegradetool.testing.Tester.register` on it.
That will add your |Tester| to the list of available |Testers| to be asked about configuration files.

|handles|
---------

|handles| will be given an already open file-like object to work with. It should return true or false depending on whether
or not this file can be parsed by this |Tester|.

.. warning:: Do **NOT** close the passed file descriptor, it will be taken care of for you.

|parse|
-------

|parse| takes a file name and returns a dictionary. All you need to do in this method is parse your configuration file
in to a dictionary. The dictionary keys must all be vaild python identifiers, because all of the key-value pairs will
be added to the **Test's** dictionary.

.. note:: Do not worry about creating a test subclass or adding to the available tests. It will all be taken care of
          :ref:`behind the scenes<testermeta-ex>`.


|start|
-------

The start method is called when it's time for your test to run. It basically is your test. Due to the :ref:`machinery<testermeta-ex>` behind
|parse|, any data you want from your configuration file will be available in as an attribute of the instance.

Additional output
+++++++++++++++++

Some times a test may want to give additional output to the user or give more detailed information to a
:py:class:`~moodlegradetool.reporting.Report`. In this case there are two optional attributes that can be included:

    output()
        A method that returns additional output as a string. This can be shown in addition to the program's source code
        on the student's result screen.

    report
        An attribute that contains a list of tuples in the format of (*name*, *value*). Name should be the name on the
        report and value will be interpreted as a boolean to show whether this part passed or not. Each item in this
        attribute will add an additional line in the report (if the :py:class:`~moodlegradetool.reporting.Report` being
        used supports it)

.. warning:: The |Tester| should not add these attributes at all if it doesn't support them

.. _testermeta-ex:

TesterMeta
++++++++++

.. note:: If all you want to do is make a |Tester|, you don't need this information. This is for those who are curious
          as to how a |Tester| becomes a **Test**

:py:class:`~moodlegradetool.testing.TesterMeta` is responsible for the magic behind the |parse| method. It replaces the
|parse| method with a substitute that will generate the subclass with dict returned by |parse| and add the resulting
class to the list of available tests.

Why make a separate class?
--------------------------

It would have been possible to create a Tester instance with the configuration. And just use that instance to test all
the students, but doing it this way allows each student to have its own test instance. That makes things like generating
reports and accessing the test results on demand much nicer.

Ok, but why a metaclass?
------------------------

There may have been more socially acceptable ways to accomplish the subclass creation, but this method appeared to be
the cleanest. It works nicely with inheritance, and its almost completely transparent, to *both* the caller and the
callee from both sides its a single method call. With this method all a |Tester| has to do is return a dictionary, it
doesn't have to worry about decorators, helper methods, or any other tricks. The api is nice and simple. It
also keeps the code behind this self-contained and in an easy to find place.