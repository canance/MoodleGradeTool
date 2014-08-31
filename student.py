__author__ = 'phillip'
#Requires enum34 from python package index

import subprocess
from enum import Enum

class Student(object):
    tests = []

    def __init__(self, name, main_class, otherclasses=None):
        self.student = name
        self.java_class = main_class
        self.classlist= otherclasses if not otherclasses is None else []

        for i in xrange(len(self.tests)):
            self.tests[i] = self.tests[i](name, main_class)

        self._state = StudentState.not_tested

    def dotests(self):
        self._state = StudentState.testing
        for test in self.tests:
            test.start()

        self._state = StudentState.ready

    def dobuild(self):
        self.proc = subprocess.Popen(('javac', "/".join(self.java_class.split(",")) + ".java"))

    @property
    def score(self):
        """
        Calculates the students score
        :return: The total score of all the tests
        :rtype: int
        """

        return reduce(lambda scr, test: scr + test.score(), self.tests, 0)

    @property
    def state(self):
        """
        The state the student object is in.

        :rtype: StudentState
        """
        return self.state


class StudentState(Enum):
    not_built = 0
    building = 1
    build_error = -1
    not_tested = 2
    testing = 3
    ready = 4

