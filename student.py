__author__ = 'phillip'
# Requires enum34 from python package index

import subprocess
from enum import Enum


class Student(object):
    tests = []

    def __init__(self, name, main_class, otherclasses=None):
        self.name = name
        self.java_class = main_class
        self.classlist = otherclasses if not otherclasses is None else []
        self.directory = os.path.abspath('./' + name)

        for i in xrange(len(self.tests)):
            self.tests[i] = self.tests[i](name, main_class)

        self._state = StudentState.not_built

    def dotests(self):
        self._state = StudentState.testing
        for test in self.tests:
            test.start()

        self._state = StudentState.ready

    def dotest(self, cls):
        for test in self.tests:
            if isinstance(test, cls):
                test.start()
            else:
                t = cls(self.name, self.java_class)
                self.tests.append(t)
                t.start()

    def dobuild(self):
        self._state = StudentState.building
        with open(self.directory + "/build.log", 'a') as f:
            #Log entry header
            log.write('\n\n' + str(datetime.datetime.now()) + '\n')
            log.write("Starting build of %s.java\n\n" % className)

            self.proc = subprocess.Popen(('javac', '.' + "/".join(self.java_class.split(",")) + ".java"),
                                         cwd=self.directory, stdout=f, stderr=subprocess.STDOUT)

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
        if self._state == StudentState.building and not self.proc.poll() is None:
            if self.proc.returncode == 0:
                self._state = StudentState.not_tested
            else:
                self._state = StudentState.build_error

        return self._state


class StudentState(Enum):
    not_built = 0
    building = 1
    build_error = -1
    not_tested = 2
    testing = 3
    ready = 4

