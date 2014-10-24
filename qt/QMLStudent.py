__author__ = 'phillip'

import __init__
import qt_wrappers
import student
import threading
import PySide.QtCore as QtCore
from PySide.QtCore import Property as QProperty, Signal, Slot, QObject, QAbstractListModel


def _sig_decorator(sig):
    def dec(func):
        def signal_function(*args, **kwargs):
            func(*args, **kwargs)
            sig.emit()
        return signal_function
    return dec

def proc_wait_sig(proc, sig):
    proc.wait()
    sig.emit()

class SourceOutput(QObject):
    name = ""
    output = ""

class QMLStudent(student.Student, QObject):

    lastid = 0
    allotedids = set()

    nameChanged = Signal()
    status_nameChanged = Signal()
    scoreChanged = Signal()
    possibleChanged = Signal()
    flagChanged = Signal()
    studentIDChanged = Signal()

    def __init__(self, **kwargs):
        super(QMLStudent, self).__init__(**kwargs)
        self._id = self.getid()

    def dobuild(self):
        super(QMLStudent, self).dobuild()
        threading.Thread(target=proc_wait_sig, args=(self.proc, self.status_nameChanged))

    def dotests(self):
        super(QMLStudent, self).dotests()
        self.scoreChanged.emit()

    def dotest(self, cls):
        super(QMLStudent, self).dotest(cls)
        self.scoreChanged.emit()
        self.possibleChanged.emit()


    @Slot()
    def reload_tests(self):
        self.tests = [qt_wrappers.TestWrapper(t(self.name, self.java_class)) for t in student.Student.tests]
        self.state = student.StudentState.testing
        self.scoreChanged.emit()
        self.possibleChanged.emit()
        self.flagChanged.emit()

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
        self.nameChanged.emit()

    def getStatus_name(self):
        states = student.StudentState
        m = {states.ready: "Testing Finished",
             states.testing: "Testing...",
             states.build_error: "Build Error",
             states.building: "Building...",
             states.not_built: "Not started",
             states.not_tested: "Waiting to test"}
        return m[self.state]

    def getFlag(self):
        s = self.state
        if s == student.StudentState.build_error:
            return "error"
        if s == student.StudentState.ready:
            return "ready"

    def getScore(self):
        if not self.state == student.StudentState.ready:
            return 0
        else:
            return self.score

    def getPossible(self):
        return self.possible

    def getStudentID(self):
        return self._id

    @property
    def sourceobject(self):
        ret = SourceOutput()
        ret.name = self.name
        ret.output = self.source
        return ret

    @student.Student.state.setter
    def state(self, st):
        self._state = st
        self.status_nameChanged.emit()
        self.flagChanged.emit()

    @classmethod
    def getid(cls):
        cur = cls.lastid + 1
        while cur in cls.allotedids:
            cur += 1
        cls.allotedids.add(cur)
        cls.lastid = cur
        return cur

    studentName = QProperty(str, getName, setName, notify=nameChanged)
    status_name = QProperty(str, getStatus_name, notify=status_nameChanged)
    totalScore = QProperty(int, getScore, notify=scoreChanged)
    totalPossible = QProperty(int, getPossible, notify=possibleChanged)
    flag = QProperty(str, getFlag, notify=flagChanged)
    studentID = QProperty(int, getStudentID, notify=studentIDChanged)

class StudentQList(QAbstractListModel):
    COL = ("studentObj", "studentName", "status_name", "totalScore", "totalPossible", "totalPossible", "flag", "studentID")
    def __init__(self, l, **kwargs):
        super(StudentQList, self).__init__(**kwargs)
        self.COL = dict(enumerate(StudentQList.COL))
        self.setRoleNames(self.COL)
        self._list = list(l)

    def rowCount(self, *args, **kwargs):
        return len(self._list)

    def data(self, index, role, *args, **kwargs):
        for rid, name in self.COL.iteritems():
            if role == rid:
                if name == "studentObj":
                    return self._list[index.row()]
                return getattr(self._list[index.row()], name)
        return None


def get_dict_attr(obj,attr):
    for obj in [obj]+obj.__class__.mro():
        if attr in obj.__dict__:
            return obj.__dict__[attr]
    raise AttributeError