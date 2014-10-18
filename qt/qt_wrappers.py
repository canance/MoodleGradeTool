__author__ = 'phillip'

from PySide.QtCore import QObject, Property as QProperty, Signal
import testing

class TestWrapper(QObject):

    testSig = Signal()

    def __init__(self, test):
        assert isinstance(test, testing.Tester)
        self._test = test

    def getHasOutput(self):
        return hasattr(self._test, 'output')

    def getOutput(self):
        return "" if not hasattr(self._test, 'output') else self._test.output

    def getScore(self):
        return self._test.score

    def getPossible(self):
        return self._test.possible

    def getName(self):
        return self._test.name

    name = QProperty(unicode, getName, notify=testSig)
    hasOutput = QProperty(bool, getHasOutput, notify=testSig)
    output = QProperty(unicode, getOutput, notify=testSig)
    score = QProperty(int, getScore, notify=testSig)
    possible = QProperty(int, getPossible, notify=testSig)