===============
Getting Started
===============

The grading folder
++++++++++++++++++

The grading folder is either a folder or zip file that contains the Java projects downloaded from Moodle. The projects can either be
single Java files or zip folders. The MoodleGradeTool will separate these in to individual student folders
automatically.

If a zip file is given, it is extracted to the parent directory of the zip file.

.. Note:: For best results extract the zip file first


The configuration folder
++++++++++++++++++++++++

The configuration folder contains everything needed to setup the tests. Test configuration files end with either
".test" or ".testx" (if it is an xml configuration). The format of the configuration file depends on the type of test
it is meant for.

If this folder is not specified, the grading folder is used.

Running the program
+++++++++++++++++++

The folders need to be setup before you run the program. There are currently two supported interfaces: a text interface
and a graphical QML interface.

Text Mode - grade.py
--------------------
The work flow for the text interface is as follows:

1. Select the grading and configuration folders
    When you start grade.py it will prompt you for the location for the folders described above. You may have to hit
    tab a couple of times to get the file path field in focus. Both of the fields support tab completion.

#. Select the tests to run
        You will be presented with a list of tests that were found; check all the ones you want to run

#. The projects are built and tested with the selected tests

#. After each student has been tested you will be presented with a results screen
        On that screen you can:
            - View the source code and test outputs
            - View the total score of the student
            - View the break down of the tests
            - Save the outputs to a file
            - Manually interact with the program

#. At then end of testing, a results.xml will be saved that contains an overall report for the class

QML Mode - qgrade.py
--------------------

A graphical interface is given to the grade tool through qml. This is an example of the main window:

.. image:: ./qml_main.png

It is separated into 4 main parts.

    1. At the top is the initial configuration. The first thing you need to do is choose
    the folders you want to use.

.. Warning:: Zip folders are not fully supported in the graphical interface yet, you need to type them in manually
..

    2. After you select your folders you need to press the *Reload Configuration* button and a list of detected tests will
    show up in the space on the right hand side of the window. When you've selected your tests,
    you need to click the *Change Selection* button to actually set them up to be used.

    3. After completing all of the above you can press *Start* to start building and testing. The students list won't actually
    show up until you get to this point. The students will change color to show you what is currently going on.

        - Gray: The student is still in processing
        - Green: The testing has been done without error
        - Red: There was a problem with this student (right now this only happens with build errors

    4. The final part at the bottom of the window gives you information about the selected student. In the list on the left
    the test results are broken down, in the list on the right the available outputs are shown. Clicking on an output
    selects it. *View Output* toggles between showing the selected output and showing the students list.

.. Note:: Currently the QML interface does not support reports or manually interacting with student programs
