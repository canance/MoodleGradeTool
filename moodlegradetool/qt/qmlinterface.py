from moodlegradetool import student
from moodlegradetool.qt import QMLStudent, qtdispatch

__author__ = 'phillip'

import PySide.QtCore as QtCore
from PySide.QtCore import QUrl
from PySide.QtGui import QApplication, QFileDialog
from PySide.QtDeclarative import QDeclarativeView

from sys import argv, exit
from moodlegradetool.qt.qt_wrappers import *
from moodlegradetool.student import Student

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
    ret.setResizeMode(QDeclarativeView.SizeRootObjectToView)
    root = ret.rootObject()
    #This sets up the file dialogs
    gradedia = QFileDialog()
    gradedia.setFileMode(QFileDialog.Directory)
    gradedia.setOption(QFileDialog.ShowDirsOnly, True)
    gradedia.fileSelected.connect(root.updateGradeFolder)

    root.gradeFolderBrowse.connect(gradedia.show)

    testdia = QFileDialog()
    testdia.setFileMode(QFileDialog.Directory)
    testdia.setOption(QFileDialog.ShowDirsOnly, True)
    testdia.fileSelected.connect(root.updateTestFolder)
    root.testFolderBrowse.connect(testdia.show)

    return app, ret, gradedia, testdia  # Return the QApplication and the QDeclarativeView


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
