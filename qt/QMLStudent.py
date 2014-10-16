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
        self.nameChanged.emit()

    @student.Student.state.setter
    def state(self, st):
        self._state = st
        self.statusChanged.emit()

def get_dict_attr(obj,attr):
    for obj in [obj]+obj.__class__.mro():
        if attr in obj.__dict__:
            return obj.__dict__[attr]
    raise AttributeError