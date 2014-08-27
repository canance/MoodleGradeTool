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

    def __init__(self, student, clsName):
        self.student = student
        self.clsName = clsName

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

    def start(self, student, clsName):
        subprocess.call(('java', clsName), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    @staticmethod
    def handlesconfig(path):
        return False

class RegexTester(Tester):

    @classmethod
    def parse_config(cls, configfile):
        ret = {}

        detect = RegexTester._detect_name
        with open(configfile) as f:
            for line in f:
                line = line.strip()

                if line[0] == "#":
                    continue  # Skip comments

                res = detect(line, ret)
                if res:
                    detect = res

        return ret

    @classmethod
    def _detect_name(cls, line, d):
        if line:
            d['name'] = line
            return cls._detect_infile

    @classmethod
    def _detect_infile(cls, line, d):
        if os.path.isfile(line):
            d['input_file'] = line
            return cls._detect_regex

    @classmethod
    def _detect_regex(cls, line, d):
        if line:
            d.setdefault('regexes', []).append(re.compile(line))
            return cls._detect_regex

    def score(self):
        pass

    def start(self):
        pass

    @staticmethod
    def handlesconfig(fd):
        return "RegexTester" in fd.readline()

    def possiblescore(self):
        pass


ManualTest.parse_config('Manual')