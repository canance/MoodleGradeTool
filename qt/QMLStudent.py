__author__ = 'phillip'

import student
from PySide.QtCore import Property as QProperty, Signal, Slot, QObject

class QMLStudent(QObject, student.Student):

    nameChanged = Signal()
    statusChanged = Signal()
    scoreChanged = Signal()
    possibleChanged = Signal()

    def getName(self):
        return self.name
    def setName(self, name):
        self.name = name