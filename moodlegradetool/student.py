"""Manages student information such as student name, available java classes, tests run and results."""

__author__ = 'phillip'
# Requires enum34 from python package index

import os
import subprocess
import datetime
from threading import Thread, Event

from enum import Enum


class StateError(Exception):
    pass


#Needs to be defined here so its ready when Student is being interpreted
def requirestate(state):
    """
    Decorator: Requires the object be in a certain state before the function can be run. An iterable can be passed
    in which case the objects state needs to match any of the elements.

    :param state: The state(s) that needs to be matched
    """
    def decorator(func):
        def checkstate(self, *args, **kwargs):
            try:
                try:
                    assert self.state in state
                except TypeError:
                    assert self.state == state
            except AssertionError as ex:
                raise StateError("{obj} is not in {state} state(s)".format(obj=repr(self), state=str(state)))
            return func(self, *args, **kwargs)

        return checkstate

    return decorator


class StudentState(Enum):
    """An enumeration of the different states student objects can be in."""
    not_built = 0  #: The program has not been built yet
    building = 1  #: The program is in the process of building
    build_error = -1  #: There was a problem during building
    not_tested = 2  #: The program built ok, but has not been tested yet
    testing = 3  #: The program is in the process of being tested
    ready = 4  #: The program has been tested


class Student(object):
    """
    Manages the java classes and tests for a particular student. Each student has a corresponding folder in the
    grading folder.

    :cvar tests: In a class context, tests holds the test classes that should be run
    :ivar tests: In an instance context, tests holds the test instances for this student
    :ivar name: The students name
    :ivar java_class: The main java class that should be tested
    :ivar classlist: Other java classes that were detected for the student
    :ivar directory: The directory for the student
    """
    tests = []

    def __init__(self, name, main_class, otherclasses=None, **kwargs):
        super(Student, self).__init__(**kwargs)
        self.name = name
        self.java_class = main_class
        self.classlist = otherclasses if not otherclasses is None else []
        self.directory = os.path.abspath('./' + name)
        self._testingfinished = Event()  # The testing event for asynchronous testing
        self.thread = None  # The testing thread

        #Instansiate the test classes provided
        #We need to make sure that we don't modify the existing list
        testers = self.tests
        self.tests = []
        for t in testers:
            self.tests.append(t(name, main_class))

        self.state = StudentState.not_built  # Set the state

    @requirestate((StudentState.not_tested, StudentState.ready))
    def async_tests(self):
        """
        Start the testing asynchronously. Use wait_tests to wait until the tests are done.

        :Requires: not_tested or ready state
        """
        self._testingfinished.clear()  # Clear the event flag
        self.thread = Thread(target=self.dotests)  # Create the thread
        self.thread.start()  # And start it

    def wait_tests(self, timeout=None):
        """
        Wait until timeout to see if testing has finished. If timeout is None wait indefinitely.

        :param timeout: The timeout value
        :return: True if testing has finished, False otherwise
        :rtype: bool
        """
        return self._testingfinished.wait(timeout)

    @requirestate((StudentState.not_tested, StudentState.ready))
    def dotests(self):
        """Performs all the tests registered with this student.

        :Requires: not_tested or ready state
        """

        self.state = StudentState.testing
        for test in self.tests:
            test.start()

        self.state = StudentState.ready
        self._testingfinished.set()

    @requirestate((StudentState.not_tested, StudentState.ready))
    def dotest(self, cls):
        """
        Performs a specific test. Adds the test to the students test list if not there already.

        :Requires: not_tested or ready states

        :param cls: The test class to perform
        """
        t = None
        #Look in the tests list
        for test in self.tests:
            if isinstance(test, cls):  # See if any of them are instances of the passed class
                t = test  # If so use the test
        if not t:
            t = cls(self.name, self.java_class)  # If not instantiate it
            self.tests.append(t)  # And add it to tests
        t.start()  # Start it

    @requirestate(StudentState.not_built)
    def dobuild(self):
        """
        Builds the program.

        :Requires: not_built state
        """

        try:
            with open(self.directory + "/build.log", 'a') as log:  # Open the log file
                #Log entry header
                log.write('\n\n' + str(datetime.datetime.now()) + '\n')
                log.write("Starting build of %s.java\n\n" % self.java_class)

                #Start the build
                self.proc = subprocess.Popen(('javac', "/".join(self.java_class.split(".")) + ".java"),
                                             cwd=self.directory, stdout=log, stderr=subprocess.STDOUT)
                self.state = StudentState.building  # Set state to building
        except Exception as ex:
            self.state = StudentState.build_error
            raise ex

    @property
    @requirestate(StudentState.ready)
    def score(self):
        """
        Calculates the students score

        :Requires: Ready state

        :return: The total score of all the tests
        :rtype: int
        """
        return reduce(lambda scr, test: scr + test.score, self.tests, 0)

    @property
    def possible(self):
        """
        Calculates the students possible score

        :return: The total possible score for all the tests
        :rtype: int
        """
        return reduce(lambda scr, test: scr + test.possible, self.tests, 0)

    @property
    def state(self):
        """
        The state the student object is in.

        :rtype: StudentState
        """
        # If the state is building we need to check to see if there was a build error
        if self._state == StudentState.building and not self.proc.poll() is None:
            if self.proc.returncode == 0:
                self.state = StudentState.not_tested  # Set state to not tested when build succeeds
            else:
                self.state = StudentState.build_error

        return self._state

    @property
    def source(self):
        """
        The source code for the main java class

        :return: Source code as string
        :rtype: str
        """
        java_path = "/".join(self.java_class.split('.'))
        with open(self.directory+"/"+java_path+".java", 'r') as f:
            ret = f.read()
        return ret

    @state.setter
    def state(self, value):
        self._state = value

    def __repr__(self):
        return "Student({}, {})".format(self.name, self.java_class)

    def __str__(self):
        return self.name + ": " + self.java_class
