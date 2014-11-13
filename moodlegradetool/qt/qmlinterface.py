

__author__ = 'phillip'

from PySide.QtCore import QUrl
from PySide.QtGui import QApplication, QFileDialog
from PySide.QtDeclarative import QDeclarativeView

from sys import argv


def initialize_view():
    app = QApplication(argv)  # Make a new QApplication
    ret = QDeclarativeView()  # Set up the declarative view

    dir = '/'.join(__file__.split('/')[:-1])

    #TODO: Need to be able to find this file regardless of the current directory
    url = QUrl.fromLocalFile(dir + "/MoodleGrade.qml")  # Make the url for the file
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
