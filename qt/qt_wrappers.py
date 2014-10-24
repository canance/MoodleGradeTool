__author__ = 'phillip'

from PySide.QtCore import QObject, Property as QProperty, Signal, QAbstractListModel
import testing

import types

def wrapped_start(self):
    self.start_bak()
    self.qt_signal.emit()

class TestWrapper(QObject):

    testSig = Signal()

    def __init__(self, test):
        super(TestWrapper, self).__init__()
        assert isinstance(test, testing.Tester)
        self._test = test
        self._test.qt_signal = self.testSig
        if not hasattr(test, 'start_bak'):
            test.start_bak = test.start
            test.start = types.MethodType(wrapped_start, test)

    def __getattr__(self, item):
        return getattr(self._test, item)

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

class ObjectListModel(QAbstractListModel):
    COL = ("Obj")
    def __init__(self, l, **kwargs):
        super(ObjectListModel, self).__init__(**kwargs)
        self.COL = dict(enumerate(ObjectListModel.COL))
        self.setRoleNames(self.COL)
        self._list = list(l)

    def rowCount(self, *args, **kwargs):
        return len(self._list)

    def data(self, index, role, *args, **kwargs):
        return self._list[index.row()]