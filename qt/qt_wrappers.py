__author__ = 'phillip'

from PySide.QtCore import QObject, Property as QProperty, Signal, QAbstractListModel
import testing

import types

def wrapped_start(self):
    self.start_bak()
    self.qt_signal.emit()

class TestClassWrapper(QObject):

    _selected = False
    nameChanged = Signal()
    selectedChanged = Signal()

    def __init__(self, test, **kwargs):
        super(TestClassWrapper, self).__init__(**kwargs)
        self.test = test

    def getName(self):
        return self.test.name

    def getSelected(self):
        return self._selected

    def setSelected(self, val):
        self._selected = val
        self.selectedChanged.emit()

    name = QProperty(str, getName, notify=nameChanged)
    selected = QProperty(bool, getSelected, setSelected, notify=selectedChanged)

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
    COL = ("Obj", "name")
    def __init__(self, l, **kwargs):
        super(ObjectListModel, self).__init__(**kwargs)
        self.COL = dict(enumerate(ObjectListModel.COL))
        self.setRoleNames(self.COL)
        self._list = list(l)

    def rowCount(self, *args, **kwargs):
        return len(self._list)

    def data(self, index, role, *args, **kwargs):
        res = None
        for rid, name in self.COL.iteritems():
            if role == rid:
                if name == "Obj":
                    res =  self._list[index.row()]
                    break
                res = self._list[index.row()].property(name)
                break
        print res
        return res
