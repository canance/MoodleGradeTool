__author__ = 'phillip'

import sys
import os.path
import qmlinterface
import qtdispatch
import grade
import QMLStudent

grade.Student = QMLStudent.QMLStudent  # Change the default student class used
sys.path.append(os.path.abspath(".."))  # Add the parent directory to the python path

studentslist = []  # Holds the main list of students
mainview = None  # Holds the main window
qapp = None  # Holds the main application
maindispatch = None  # Holds the main QtDispatcher

mainthread = None  # Holds the main thread


def initialize_view():
    """
        Ths method is responsible for setting up the main window.
        It stores the QApplication and the QDeclarative view in qapp and mainview
    """
    global qapp, mainview
    qapp, mainview = qmlinterface.initialize_view()
