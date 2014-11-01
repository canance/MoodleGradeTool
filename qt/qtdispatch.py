__author__ = 'phillip'

from PySide.QtCore import QObject, Slot, Signal
from PySide.QtGui import QFileDialog
import __init__
from QMLStudent import StudentQList, QMLStudent
from student import StudentState
from qt_wrappers import TestWrapper, TestClassWrapper, ObjectListModel
from testing import findtests, tests
from grade import prepare_directory
import os
from contextlib import contextmanager
from types import MethodType

@contextmanager
def DisconnectSignal(signal, slot):
    signal.disconnect(slot)
    try:
        yield
    finally:
        signal.connect(slot)

class QTDispatcher(QObject):

    resultsUpdated = Signal(ObjectListModel)
    outputsUpdated = Signal(ObjectListModel)
    testsUpdated = Signal(ObjectListModel)
    studentsUpdated = Signal(StudentQList)


    def __init__(self, view, **kwargs):
        super(QTDispatcher, self).__init__(**kwargs)
        self._view = view
        self._root = view.rootObject()

        self.testwrappers = None

        root = self._root
        root.studentSelected.connect(self.studentchanged)
        root.parseTests.connect(self.parsetests)
        root.startTesting.connect(self.starttests)
        root.gradeFolderBrowse.connect(self.gradebrowse)
        root.testFolderBrowse.connect(self.testbrowse)
        root.setupTests.connect(self.setuptests)

        self.resultsUpdated.connect(root.updateTestResults)
        self.outputsUpdated.connect(root.updateOutputs)
        self.testsUpdated.connect(root.updateTestList)
        self.studentsUpdated.connect(root.updateStudents)

        self.gradedia = QFileDialog()
        self.gradedia.setFileMode(QFileDialog.Directory)
        self.gradedia.setOption(QFileDialog.ShowDirsOnly, True)
        self.gradedia.fileSelected.connect(root.updateGradeFolder)

        self.testdia = QFileDialog()
        self.testdia.setFileMode(QFileDialog.Directory)
        self.testdia.setOption(QFileDialog.ShowDirsOnly, True)
        self.testdia.fileSelected.connect(root.updateTestFolder)
        self.oldgrade = ""



    @Slot(int)
    def studentchanged(self, id):
        curStudent = None
        for student in __init__.studentslist:
            if student.getStudentID() == id:
                curStudent = student
                break

        self.resultsUpdated.emit(ObjectListModel([TestWrapper(t) for t in curStudent.tests]))
        outputs = [curStudent.sourceobject] + [TestWrapper(t) for t in curStudent.tests if hasattr(t, 'output')]
        self.outputsUpdated.emit(ObjectListModel(outputs))


    @Slot()
    def parsetests(self):
        with DisconnectSignal(self._root.parseTests, self.parsetests):
            path = self._root.property('testFolder')
            findtests(str(path))
            self.testwrappers = [TestClassWrapper(t) for t in tests.itervalues()]
            self.testsUpdated.emit(ObjectListModel(self.testwrappers))


    @Slot()
    def starttests(self):
        with DisconnectSignal(self._root.startTesting, self.starttests):

            if self.oldgrade != self._root.property('gradeFolder'):
                self.oldgrade = self._root.property('gradeFolder')
                os.chdir(self.oldgrade)
                self.populate_students()

            for student in __init__.studentslist:
                student.status_nameChanged.connect(self.starttest)
                student.dobuild()


    @Slot(QObject)
    def starttest(self, student):
        if student.state == StudentState.build_error:
            student.status_nameChanged.disconnect(self.starttest)
        if student.state == StudentState.not_tested:
            student.dotests()

    @Slot()
    def setuptests(self):
        with DisconnectSignal(self._root.setupTests, self.setuptests):
            QMLStudent.tests = [t.test for t in self.testwrappers if t._selected]
            for s in __init__.studentslist:
                s.reload_tests()

    @Slot()
    def populate_students(self):
        __init__.studentslist = prepare_directory(str(self._root.property('gradeFolder')))
        self.studentsUpdated.emit(StudentQList(__init__.studentslist))


    @Slot()
    def gradebrowse(self):
        self.gradedia.show()

    @Slot()
    def testbrowse(self):
        self.testdia.show()
