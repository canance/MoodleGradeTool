.. Substitutions

.. |Student| replace:: :py:class:`~moodlegradetool.student.Student`

================
Program Overview
================

This page is indented to give an overall view of how all the program pieces fit together. It's mainly a way for
developers to get there bearings in the source code.

Main Flow
+++++++++

The overall flow of the program is as follows:

    1. Get the grading and configuration (also sometimes called 'tests') folder from the user

    #. Find all the :doc:`test configuration files<usingtesters>` and make :py:class:`classes<moodlegradetool.testing.Tester>` for them

    #. Select the needed tests, and attach them to the tests attribute of the |Student| class

    #. Parse the student projects in the grading folder and make |Student| objects

    #. Do builds

    #. Perform the tests

    #. Give results to user and if applicable generate a :py:class:`~moodlegradetool.reporting.Report`

Tester objects
++++++++++++++

Every type of test needs to inherit from the :py:class:`~moodlegradetool.testing.Tester` class. These classes are then
subclassed dynamically when a supported configuration is encountered. The convention followed in code is that the generic
classes are called **Testers** and the subclasses generated from the configuration files are called **Tests**.

The process is described in more detail in :doc:`testers` but for now keep in mind **Tester** classes describe the method
in which to test and **Test** classes are specific tests for that particular program using the methods described in its
parent class.

Student objects
+++++++++++++++

|Student| objects keep track of the classes and tests for one particular student. Every student has a list containing
instances of Tests. Running tests and keeping track of scores are done through |Student| objects, they are the workhorses.

Report objects
++++++++++++++

:py:class:`~moodlegradetool.reporting.Report` objects can take the list of students and save the results in some format.




