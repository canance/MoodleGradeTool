__author__ = 'phillip'
# Requires enum34 from python package index

import os
import subprocess
import datetime

from enum import Enum


class Student(object):
    tests = []

    def __init__(self, name, main_class, otherclasses=None):
        self.name = name
        self.java_class = main_class
        self.classlist = otherclasses if not otherclasses is None else []
        self.directory = os.path.abspath('./' + name)

        #Instansiate the test classes provided
        #We need to make sure that we don't modify the existing list
        testers = self.tests
        self.tests = []
        for t in testers:
            self.tests.append(t(name, main_class))

        self._state = StudentState.not_built  # Set the state

    def dotests(self):
        """Performs all the tests registered with this student."""

        self._state = StudentState.testing
        for test in self.tests:
            test.start()

        self._state = StudentState.ready

    def dotest(self, cls):
        """
        Performs a specific test. Adds the test to the students test list if not there already.
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

    def dobuild(self):
        """
        Builds the program.
        """
        self._state = StudentState.building  # Set state to building
        with open(self.directory + "/build.log", 'a') as log:  # Open the log file
            #Log entry header
            log.write('\n\n' + str(datetime.datetime.now()) + '\n')
            log.write("Starting build of %s.java\n\n" % self.java_class)

            #Start the build
            self.proc = subprocess.Popen(('javac', "/".join(self.java_class.split(".")) + ".java"),
                                         cwd=self.directory, stdout=log, stderr=subprocess.STDOUT)

    @property
    def score(self):
        """
        Calculates the students score
        :return: The total score of all the tests
        :rtype: int
        """
        return reduce(lambda scr, test: scr + test.score, self.tests, 0)

    @property
    def state(self):
        """
        The state the student object is in.

        :rtype: StudentState
        """
        if self._state == StudentState.building and not self.proc.poll() is None:
            if self.proc.returncode == 0:
                self._state = StudentState.not_tested
            else:
                self._state = StudentState.build_error

        return self._state


class StudentState(Enum):
    not_built = 0  # The program has not been build yet
    building = 1  # The program is in the process of building
    build_error = -1  # There was a problem during building
    not_tested = 2  # The program built ok, but has not been tested yet
    testing = 3  # The program is in the process of being tested
    ready = 4  # The program has been tested

