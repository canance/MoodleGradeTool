"""This module holds the main interface between QML and python code"""

__author__ = 'phillip'

import os
from contextlib import contextmanager
from time import sleep

from PySide.QtCore import QObject, Slot, Signal

import __init__
from QMLStudent import StudentQList, QMLStudent
from ..student import StudentState
from qt_wrappers import TestWrapper, TestClassWrapper, ObjectListModel
from ..testing import findtests, tests
from grade import prepare_directory


@contextmanager
def DisconnectSignal(signal, slot):
    """ DisconnectSignal(signal, slot)
    Context manager that will disconnect and reconnect a signal-slot pair.

    :param signal: The signal to manage
    :param slot: The slot to manage
    """
    signal.disconnect(slot)  # Disconnect the signal
    try:
        yield  # Return control
    finally:
        signal.connect(slot)  # Reconnect the signal


class QTDispatcher(QObject):
    """Responsible for receiving signals from QML and passing the results back to QML"""

    # Signals to update the interface
    resultsUpdated = Signal(ObjectListModel)
    outputsUpdated = Signal(ObjectListModel)
    testsUpdated = Signal(ObjectListModel)
    studentsUpdated = Signal(StudentQList)

    def __init__(self, view, **kwargs):
        # Do not forget to initialize the QObject or you will make puppies yowl
        super(QTDispatcher, self).__init__(**kwargs)
        self._view = view  # Get the view
        self._root = view.rootObject()  # Get the root object

        self.testwrappers = None  # Placeholder for the test results

        #Connect the view's signals to our functions
        root = self._root
        root.studentSelected.connect(self.studentchanged)
        root.parseTests.connect(self.parsetests)
        root.startTesting.connect(self.dobuilds)
        #root.gradeFolderBrowse.connect(self.gradebrowse)
        #root.testFolderBrowse.connect(self.testbrowse)
        root.setupTests.connect(self.setuptests)

        #Connect our signals to the update functions
        self.resultsUpdated.connect(root.updateTestResults)
        self.outputsUpdated.connect(root.updateOutputs)
        self.testsUpdated.connect(root.updateTestList)
        self.studentsUpdated.connect(root.updateStudents)

        self.oldgrade = ""
        self._cache = {}  # KeepAlive cache for objects sent to QML


    @Slot(int)
    def studentchanged(self, id):
        """
        Slot: Handles different student records being selected. It finds the matching student object, and passes
        detailed test results and outputs back to QML through the resultsUpdated and outputsUpdated signals.

        :param id: The id of the selected student
        """
        curStudent = None
        # Search the students list for a student with the matching ID
        for student in __init__.studentslist:
            if student.getStudentID() == id:
                curStudent = student  # Store the student
                break
        #Send the test results
        l = ObjectListModel([TestWrapper(t) for t in curStudent.tests])
        l.moveToThread(__init__.mainthread)
        self.resultsUpdated.emit(l)
        self._cache["results"] = l
        #Get the tests that have outputs and add it too the source output object
        outputs = [curStudent.sourceobject] + [TestWrapper(t) for t in curStudent.tests if hasattr(t, 'output')]
        l = ObjectListModel(outputs)
        l.moveToThread(__init__.mainthread)
        self.outputsUpdated.emit(l)  # Send the outputs
        self._cache["outputs"] = l


    @Slot()
    def parsetests(self):
        """
        Slot: Parses the test configuration files, passes the available test back through testsUpdated signal
        """
        # Disconnect this slot while the function is running
        with DisconnectSignal(self._root.parseTests, self.parsetests):
            path = self._root.property('testFolder')  # Get the configuration folder from the view
            findtests(str(path))  # Parse the test files
            self.testwrappers = [TestClassWrapper(t) for t in tests.itervalues()]  # Wrap the test classes
            l = ObjectListModel(self.testwrappers)
            l.moveToThread(__init__.mainthread)
            self.testsUpdated.emit(l)  # Send the
            self._cache['tests'] = l


    @Slot()
    def dobuilds(self):
        """
        Slot: Performs the student builds and sets the tests to start when the build is finished. See starttest.
        """
        # Disconnect this slot while the function is running
        with DisconnectSignal(self._root.startTesting, self.dobuilds):
            #See if the folder to grade has changed
            if self.oldgrade != self._root.property('gradeFolder'):
                self.oldgrade = self._root.property('gradeFolder')  # If so store the new folder
                os.chdir(self.oldgrade)  # Change to that directory
                self.populate_students()  # And reset the students list
            for student in __init__.studentslist:  # For every student
                #Connect the status changed signal to the starttest slot
                student.status_nameChanged.connect(self.starttest)
                student.dobuild()  # And start the build


    @Slot(QObject)
    def starttest(self, student):
        """
        Slot: Starts the tests. This slot is connected by dobuilds when the build is started.

        :param student: The student that sent the signal
        """
        # Disconnect the signal if there was either a build error or if the build was finished
        if student.state == StudentState.build_error or student.state == StudentState.not_tested:
            student.status_nameChanged.disconnect(self.starttest)
        if student.state == StudentState.not_tested:
            student.async_tests()  # Do the tests if we're ready

    @Slot()
    def setuptests(self):
        """
        Slot: This will setup the tests selected to be run. It updates the student class's test list and calls
        reload tests on all the students
        """
        # Disconnect the signal while the function is running
        with DisconnectSignal(self._root.setupTests, self.setuptests):
            #Get every test that was selected in the interface
            QMLStudent.tests = [t.test for t in self.testwrappers if t._selected]
            for s in __init__.studentslist:  # And for every student
                s.reload_tests()  # Reload the tests

    @Slot()
    def populate_students(self):
        """
        Slot: Detects all the students in the grading folder. Calls prepare_directory and returns the students list
        through the studentsUpdated signal
        """
        # Get the grade folder and prepare the directory
        __init__.studentslist = prepare_directory(str(self._root.property('gradeFolder')))
        l = StudentQList(__init__.studentslist)
        l.moveToThread(__init__.mainthread)
        self.studentsUpdated.emit(l)  # Send the updated list
        self._cache["students"] = l