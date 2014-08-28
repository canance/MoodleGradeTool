__author__ = 'phillip'

import sys, os

import re
import subprocess
import abc


testers = set() # The available test types

tests = {} # The available tests

class TesterMeta(abc.ABCMeta):

    def __init__(cls, clsname, bases, attr):
        super(TesterMeta, cls).__init__(clsname, bases, attr)

        parser = cls.parse_config # Get the classes parse config_function

        @classmethod
        def load_config(clss, configfile):  # This will replace parse_config on the class
            attrs = cls.__dict__.copy()  # Copy the class's dict
            attrs.update(parser(configfile))  # Update the copy with the parsed config file
            name = attrs['name']  # Get the tests name
            tests[name] = type(name, (cls, ), attrs)  # Create the subclass for the test and register it

        cls.parse_config = load_config  # Replace the class's parse_config


class Tester(object):
    __metaclass__ = TesterMeta

    cwd = '.'

    def __init__(self, student, clsName):
        self.student = student
        self.clsName = clsName
        self.cwd = self.cwd.format(student=student, cls=clsName)

    @abc.abstractmethod
    def start(self):
        pass

    @classmethod
    def register(cls):
        """Registers the class with the main program. When registered this class will be asked if it supports
        any found configuration files."""
        testers.add(cls)

    @classmethod
    @abc.abstractmethod
    def parse_config(cls, configfile):
        """Parse the configuration and return a dict. The elements in the dict will added to the test class's dict.
        Tester handles making the dict elements available, subclassing for the particular test, and registering the
        :param cls:
        test. A name key should be in the dict that has the tests name."""
        return {}

    @abc.abstractmethod
    def score(self):
        pass

    @abc.abstractmethod
    def possiblescore(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def handlesconfig(fd):
        """
        Returns true if the config in the file object is handled by this Tester.

        :param fd: A file object for the config file
        """
        return False

    def failed(self):
        return self.score() == self.possiblescore()

class ManualTest(Tester):

    @classmethod
    def parse_config(cls, configfile):
        return {'name': configfile}

    def score(self):
        return 1

    def possiblescore(self):
        return 1

    def start(self):
        subprocess.call(('java', self.clsName), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, cwd=self.cwd)

    @staticmethod
    def handlesconfig(path):
        return False

class RegexTester(Tester):

    @classmethod
    def parse_config(cls, configfile):
        ret = {}

        detectors = (cls._detect_name, cls._detect_infile,  cls._detect_regex)
        with open(configfile) as f:
            for line in f:
                line = line.strip()

                if line and line[0] == "#":
                    continue  # Skip comments
                for func in detectors:
                    if func(line, ret):
                        break

        return ret

    @classmethod
    def _detect_name(cls, line, d):
        if line and not d.has_key('name'):
            d['name'] = line
            return True

    @classmethod
    def _detect_infile(cls, line, d):
        if (not d.has_key('input_file')) and os.path.isfile(line):
            d['input_file'] = line
            return True

    @classmethod
    def _detect_regex(cls, line, d):
        if line and line[:7] == "Regex: ":
            line = line[6:]
            d.setdefault('regexes', []).append(re.compile(line))
            return True

    def score(self):
        return self._score

    def start(self):
        self._score = 0
        with open(self.input_file) as f:
            self._output = subprocess.check_output(('java', self.clsName), stdin=f, cwd=self.cwd)

        for reg in self.regexes:
            m = reg.search(self._output)
            if m:
                self._score += 1

    @staticmethod
    def handlesconfig(fd):
        return "RegexTester" in fd.readline()

    def possiblescore(self):
        return len(self.regexes)


ManualTest.parse_config('Manual')