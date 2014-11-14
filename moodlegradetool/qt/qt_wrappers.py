"""Contains various simple wrapper classes to expose qt unaware classes to qt"""

from moodlegradetool import testing

__author__ = 'phillip'

from PySide.QtCore import QObject, Property as QProperty, Signal, QAbstractListModel

import types


def wrapped_start(self):
    """
    Replacement start method to emit a signal after the test has been run, Gets attached to tests by TestWrapper
    """
    self.start_bak()  # Start the original start method
    self.qt_signal.emit()  # Emit the signal when done


class TestClassWrapper(QObject):
    """
    A wrapper for test class objects. Used in the test selection list.

    """
    _selected = False  # See if we've been selected
    nameChanged = Signal()  #: Fires when the tests name has been changed
    selectedChanged = Signal()  #: Fires when the tests selection has changed

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
    name = QProperty(str, getName, notify=nameChanged)  #: Qproperty for the test name
    selected = QProperty(bool, getSelected, setSelected, notify=selectedChanged)  #: QProperty indicating the user has selected it


class TestWrapper(QObject):
    """Wraps actual test objects for qt. This also replaces the start method on the wrapped test so it signals when
    ever the test is done.

    """
    testSig = Signal()  #: Signal to specify the test information has changed

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

    name = QProperty(unicode, getName, notify=testSig)  #: QProperty for the test's name
    hasOutput = QProperty(bool, getHasOutput, notify=testSig)  #: QProperty to check to see if the test has output
    output = QProperty(unicode, getOutput, notify=testSig)  #: QProperty to get the actual output
    score = QProperty(int, getScore, notify=testSig)  #: QProperty for the students score on the test
    possible = QProperty(int, getPossible, notify=testSig)  #: QProperty for the test's possible score


class ObjectListModel(QAbstractListModel):
    """
    Generic data model for any QObject. Wraps a python list of QObjects to allow for display in a QML List view.
    """
    _COL = ("Obj", "name")

    def __init__(self, l, **kwargs):
        super(ObjectListModel, self).__init__(**kwargs)
        self._COL = dict(enumerate(ObjectListModel._COL))
        self.setRoleNames(self._COL)
        self._list = list(l)

    def rowCount(self, *args, **kwargs):
        """
        The number of rows in the model.

        :param args: Additional arguments
        :param kwargs: Additional keyword arguments
        :return: The length of the list
        :rtype: int
        """
        return len(self._list)

    def data(self, index, role, *args, **kwargs):
        """
        Gets the object corresponding to the given index and role. Only one role is valid "Obj"

        :param index: The index of the object
        :param role: The role of the data
        :param args: Additional arguments
        :param kwargs: Additional keyword arguments
        :return: The object or none if not found
        :rtype: QObject
        """
        res = None
        for rid, name in self._COL.iteritems():
            if role == rid:
                if name == "Obj":
                    res = self._list[index.row()]
                    break
                res = self._list[index.row()].property(name)
                break
        return res
