__author__ = 'phillip'

from PySide.QtCore import QObject, Property as QProperty, Signal, QAbstractListModel
import testing

import types


def wrapped_start(self):
    """
    Replacement start method to emit a signal after the test has been run
    """
    self.start_bak()
    self.qt_signal.emit()


class TestClassWrapper(QObject):
    """
    A wrapper for test class objects. Used for selecting the tests to run.

    """
    _selected = False  # See if we've been selected
    nameChanged = Signal()
    selectedChanged = Signal()

    def __init__(self, test, **kwargs):
        super(TestClassWrapper, self).__init__(**kwargs)  # For the love of God, do NOT forget to initialize the QObject
        self.test = test

    # Getters and setters for QProperties
    def getName(self):
        return self.test.name

    def getSelected(self):
        return self._selected

    def setSelected(self, val):
        self._selected = val
        self.selectedChanged.emit()

    #Setup QProperties
    name = QProperty(str, getName, notify=nameChanged)
    selected = QProperty(bool, getSelected, setSelected, notify=selectedChanged)


class TestWrapper(QObject):
    testSig = Signal()  # Signal to specify the test information has changed

    def __init__(self, test):
        #Forget to initialize the QObject at your own peril
        super(TestWrapper, self).__init__()
        assert isinstance(test, testing.Tester)  # Make sure we have the right type
        self._test = test  # Store the test
        self._test.qt_signal = self.testSig  # Add the test signal to the test object
        if not hasattr(test, 'start_bak'):  # If it hasn't been already
            test.start_bak = test.start  # Patch the start method of the test
            test.start = types.MethodType(wrapped_start, test)

    def __getattr__(self, item):
        return getattr(self._test, item)  # Any attribute we don't have check to see if the stored test does

    def getHasOutput(self):
        return hasattr(self._test, 'output')

    def getOutput(self):
        return "" if not hasattr(self._test, 'output') else self._test.output()

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
    """
    Generic data model for any QObject.
    """
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
                    res = self._list[index.row()]
                    break
                res = self._list[index.row()].property(name)
                break
        return res
