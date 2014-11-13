from moodlegradetool import filemanager
from moodlegradetool.qt import QMLStudent, qmlinterface

__author__ = 'phillip'

import sys
import os.path

filemanager.Student = QMLStudent.QMLStudent  # Change the default student class used
sys.path.append(os.path.abspath(".."))  # Add the parent directory to the python path

studentslist = []  # Holds the main list of students
mainview = None  # Holds the main window
qapp = None  # Holds the main application
maindispatch = None  # Holds the main QtDispatcher
gradedia = None
testdia = None

mainthread = None  # Holds the main thread


def initialize_view():
    """
        Ths method is responsible for setting up the main window.
        It stores the QApplication and the QDeclarative view in qapp and mainview
    """
    global qapp, mainview, gradedia, testdia
    qapp, mainview, gradedia, testdia = qmlinterface.initialize_view()
