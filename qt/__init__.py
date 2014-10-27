__author__ = 'phillip'

import sys
import os.path
import qmlinterface
import qtdispatch
import grade
import QMLStudent

grade.Student = QMLStudent.QMLStudent
sys.path.append(os.path.abspath(".."))

studentslist = []
mainview = None
qapp = None
maindispatch = None

mainthread = None

def initalize_view():
    global qapp, mainview
    qapp, mainview = qmlinterface.initalize_view()
