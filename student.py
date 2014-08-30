__author__ = 'phillip'
#Requires enum34 from python package index

from enum import Enum

class Student(object):
    tests = []

    def __init__(self, name, main_class):
        self.student = name
        self.java_class = main_class

        for i in xrange(len(self.tests)):
            self.tests[i] = self.tests[i](name, main_class)

        self._state = StudentState.not_tested

    def dotests(self):
        self._state = StudentState.testing
        for test in self.tests:
            test.start()

        self._state = StudentState.ready

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
    not_tested = 0
    testing = 1
    ready = 2

