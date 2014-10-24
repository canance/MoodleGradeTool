__author__ = 'phillip'

import PySide.QtCore as QtCore
from PySide.QtCore import QUrl, QObject, Signal
from PySide.QtGui import QApplication
from PySide.QtDeclarative import QDeclarativeView

import PySide.QtDeclarative
import QMLStudent
import student
from sys import argv, exit
from qt_wrappers import *
from student import Student

app = None
mainview = None
mainctx = None

class AppData(QObject):
    _test_students = [QMLStudent.QMLStudent(name="Phillip", main_class="Lab1")]
    _students = QMLStudent.StudentQList(_test_students)
    _tests = []
    _outputs = []
    _sourceText = "MoodleGradeSource"

    studentsChanged = Signal()
    testsChanged = Signal()
    sourceTextChanged = Signal()

    def getStudents(self):
        return self._students

    def getTests(self):
        return self._tests

    def setTests(self, value):
        if isinstance(value, Student):
            self._tests = value.tests
        else:
            self._tests = value
        self._outputs = []
        for t in self._tests:
            if t.getHasOutput():
                self._outputs.append(t)
        self.testsChanged.emit()

    def getOutputs(self):
        return self._outputs

    def getSourceText(self):
        return self._sourceText

    def setSourceText(self, value):
        self._sourceText = value
        self.sourceTextChanged.emit()

    students = QProperty(QtCore.QAbstractListModel, getStudents, notify=studentsChanged)
    tests = QProperty(list, getTests, setTests, notify=testsChanged)
    outputs = QProperty(list, getOutputs, notify=testsChanged)
    sourceText = QProperty(unicode, getSourceText, setSourceText, notify=sourceTextChanged)

AppData = AppData()



def initalize_view():
    global mainview, mainctx, app
    if not mainview is None:
        return mainview
    app = QApplication(argv)
    mainview = QDeclarativeView()
    url = QUrl.fromLocalFile("./MoodleGrade.qml")
    mainview.setSource(url)
    mainctx = mainview.rootContext()
    root = mainview.rootObject()
    root.updateStudents(AppData._students)


if __name__ == "__main__":
    initalize_view()
    mainview.show()
    AppData.setSourceText("Update Test")
    stud = AppData._test_students[0]
    stud.setName("Phillip Wall")
    stud.state = student.StudentState.ready
    exit(app.exec_())
