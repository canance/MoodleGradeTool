__author__ = 'phillip'

from PySide.QtCore import QObject, Slot
from PySide.QtGui import QFileDialog
from __init__ import studentslist
from qt_wrappers import TestWrapper, ObjectListModel
from testing import findtests
from types import MethodType



class QTDispatcher(QObject):

    def __init__(self, view, **kwargs):
        super(QTDispatcher, self).__init__(**kwargs)
        self._view = view
        self._root = view.RootObject()
        root = self._root
        root.studentSelected.connect(self.studentchanged)
        root.parseTests.connect(self.parsetests)
        root.startTesting.connect(self.starttests)
        root.gradeFolderBrowse(self.gradebrowse)
        root.testFolderBrowse(self.testbrowse)

    # signal parseTests()
    # signal startTesting()
    # signal gradeFolderBrowse()
    # signal testFolderBrowse()

    @Slot(int)
    def studentchanged(self, id):
        curStudent = None
        for student in studentslist:
            if student.getStudentId() == id:
                curStudent = student
                break
        self._root.updateTestResults(ObjectListModel([TestWrapper(t) for t in studentslist]))
        outputs = [curStudent.sourceobject] + [TestWrapper(t) for t in studentslist if hasattr(t, 'output')]
        self._root.updateOutputs(outputs)


    @Slot
    def parsetests(self):
        self._root.parseTests.disconnect(self.parsetests)
        path = self._root.testFolder
        findtests(path)
        self._root.parseTests.connect(self.parsetests)

    @Slot
    def starttests(self):
        self._root.startTesting.disconnect(self.starttests)
        for student in studentslist:
            student.dotests()
        self._root.startTesting.connect(self.starttests)


    @Slot
    def gradebrowse(self):
        self._root.gradeFolderBrowse.disconnect(self.gradebrowse)
        dia = QFileDialog()
        dia.FileMode = 2
        dia.options(1)
        dia.fileSelected.connect(self._root.updateGradeFolder)
        self._root.gradeFolderBrowse.connect(self.gradebrowse)

    @Slot
    def testbrowse(self):
        self._root.testFolderBrowse.disconnect(self.testbrowse)
        pass
        self._root.testFolderBrowse.connect(self.testbrowse)