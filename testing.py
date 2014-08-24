__author__ = 'phillip'

import sys
import subprocess

class ManualTest(object):

    def start(self, student, clsName):
        subprocess.call(('java', className), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    @classmethod
    def register(cls):
        pass

    @staticmethod
    def handlesconfig(path):
        return False