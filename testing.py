__author__ = 'phillip'

import sys
import subprocess
import abc

testers = set()

tests = {}

class TesterMeta(abc.ABCMeta):

    def __init__(cls, clsname, bases, attr):
        super(TesterMeta, cls).__init__(clsname, bases, attr)

        parser = cls.parse_config

        @staticmethod
        def load_config(configfile):
            attrs = cls.__dict__.copy()
            attrs.update(parser(configfile))
            name = attrs['name']
            tests[name] = type(name, (cls, ), attrs)

        cls.parse_config = load_config


class Tester(object):
    __metaclass__ = TesterMeta

    @abc.abstractmethod
    def start(self, student, clsName):
        pass

    @classmethod
    def register(cls):
        """Registers the class with the main program. A name attribute must be defined before this method
        can be called."""
        testers.add(cls)

    @staticmethod
    @abc.abstractmethod
    def parse_config(configfile):
        """Parse the configuration and return a dict. The elements in the dict will become part of self.
        Tester handles making the dict elements available, subclassing for the particular test, and registering the
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
    def handlesconfig(path):
        return False


class ManualTest(Tester):

    @staticmethod
    def parse_config(configfile):
        return {'name': configfile}

    def score(self):
        return 1

    def possiblescore(self):
        return 1

    def start(self, student, clsName):
        subprocess.call(('java', className), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    @staticmethod
    def handlesconfig(path):
        return False


ManualTest.parse_config("Manual")