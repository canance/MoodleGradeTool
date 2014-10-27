__author__ = 'phillip'

from PySide.QtCore import QObject, Slot, Signal
from PySide.QtGui import QFileDialog
import __init__
from QMLStudent import StudentQList, QMLStudent
from qt_wrappers import TestWrapper, TestClassWrapper, ObjectListModel
from testing import findtests, tests
from grade import prepare_directory
import os
from types import MethodType



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
            if student.getStudentId() == id:
                curStudent = student
                break

        self.resultsUpdated.emit(ObjectListModel([TestWrapper(t) for t in curStudent.tests]))
        outputs = [curStudent.sourceobject] + [TestWrapper(t) for t in curStudent.tests if hasattr(t, 'output')]
        self.outputsUpdated.emit(ObjectListModel(outputs))


    @Slot()
    def parsetests(self):
        self._root.parseTests.disconnect(self.parsetests)
        path = self._root.property('testFolder')
        findtests(str(path))
        self.testwrappers = [TestClassWrapper(t) for t in tests.itervalues()]
        self.testsUpdated.emit(ObjectListModel(self.testwrappers))
        self._root.parseTests.connect(self.parsetests)

    @Slot()
    def starttests(self):
        self._root.startTesting.disconnect(self.starttests)

        if self.oldgrade != self._root.property('gradeFolder'):
            self.oldgrade = self._root.property('gradeFolder')
            os.chdir(self.oldgrade)
            self.populate_students()

        for student in __init__.studentslist:
            student.dobuild()
            student.dotests()
        self._root.startTesting.connect(self.starttests)

    @Slot()
    def setuptests(self):
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
