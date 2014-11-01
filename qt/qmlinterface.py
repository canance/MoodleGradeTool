__author__ = 'phillip'

import PySide.QtCore as QtCore
from PySide.QtCore import QUrl, QObject, Signal
from PySide.QtGui import QApplication
from PySide.QtDeclarative import QDeclarativeView

import PySide.QtDeclarative
import QMLStudent
import student
import qtdispatch
from sys import argv, exit
from qt_wrappers import *
from student import Student

app = None
mainview = None
mainctx = None


class AppData(QObject):
    """
    Holds application data for the main view.
    Deprecated in favor of the new way of communicating
    """
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


def initialize_view():
    app = QApplication(argv)  # Make a new QApplication
    ret = QDeclarativeView()  # Set up the declarative view

    #TODO: Need to be able to find this file regardless of the current directory
    url = QUrl.fromLocalFile("./qt/MoodleGrade.qml")  # Make the url for the file
    ret.setSource(url)  # Load the QML file
    return app, ret  # Return the QApplication and the QDeclarativeView


if __name__ == "__main__":
    #This section is meant as a quick test of the declarative view. To actually use it run qmoodletool in main directory
    app, mainview = initialize_view()
    mainview.updateStudentsList(AppData.getStudents())
    mainview.show()
    AppData.setSourceText("Update Test")
    stud = AppData._test_students[0]
    stud.setName("Phillip Wall")
    stud.state = student.StudentState.ready
    dispatch = qtdispatch.QTDispatcher(mainview)
    exit(app.exec_())
