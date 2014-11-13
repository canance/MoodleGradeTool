
__author__ = 'phillip'

import threading

from PySide.QtCore import Property as QProperty, Signal, Slot, QObject, QAbstractListModel

from .. import student
from sourceformatting import SourceOutput


def proc_wait_sig(proc, sig, owner):
    """
    Waits for a subprocess to finish and then fires the given signal. The signal should be able
    to accept the given owner
    :param proc: The subprocess to wait for
    :param sig: The signal to fire
    :param owner: The object to send as the signals owner
    """
    proc.wait()
    sig.emit(owner)


class QMLStudent(student.Student, QObject):
    """
    A wrapper class to make the base student available to QML.
    """
    lastid = 0  # Class variable to handle issuing ids
    allottedids = set()  # Class var to store already assigned ids

    #Signals to handle property changes
    nameChanged = Signal()
    status_nameChanged = Signal(QObject)
    scoreChanged = Signal()
    possibleChanged = Signal()
    flagChanged = Signal()
    studentIDChanged = Signal()

    def __init__(self, *args, **kwargs):
        #Initialize base classes
        super(QMLStudent, self).__init__(*args, **kwargs)
        self._id = self.getid()  # Get an id for this class

    def dobuild(self):
        super(QMLStudent, self).dobuild()  # Call super method
        #Spin up a new thread to wait on the build
        threading.Thread(target=proc_wait_sig, args=(self.proc, self.status_nameChanged, self)).start()

    def dotests(self):
        super(QMLStudent, self).dotests()  # Call super method
        #Fire appropriate signals
        self.scoreChanged.emit()

    def dotest(self, cls):
        super(QMLStudent, self).dotest(cls)  # Call super methods
        #Fire appropriate signals
        self.scoreChanged.emit()
        self.possibleChanged.emit()


    @Slot()
    def reload_tests(self):
        """
        Reload our tests based on the new tests in the class variable.
        """
        #Reinitalize the tests
        self.tests = [t(self.name, self.java_class) for t in student.Student.tests]
        self.state = student.StudentState.not_tested  #Reset our state
        #Fire all appropriate signals
        self.scoreChanged.emit()
        self.possibleChanged.emit()
        self.flagChanged.emit()

    #Getters and setters for the QProperties
    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
        self.nameChanged.emit()

    def getStatus_name(self):
        """
        Returns a user friendly state name based on the current state
        :return: State name
        :rtype: str
        """
        states = student.StudentState
        #Mapping from state to string
        m = {states.ready: "Testing Finished",
             states.testing: "Testing...",
             states.build_error: "Build Error",
             states.building: "Building...",
             states.not_built: "Not started",
             states.not_tested: "Waiting to test"}
        return m[self.state]

    def getFlag(self):
        """
        Handles letting the user interface what general state we are in.
        There are currently three states base state(""), testing is finished("ready"), there was an error("error")
        :return: String representing our state
        :rtype: str
        """
        s = self.state
        if s == student.StudentState.build_error:
            return "error"
        if s == student.StudentState.ready:
            return "ready"
        return ""

    def getScore(self):
        if not self.state == student.StudentState.ready:
            return 0
        else:
            return self.score

    def getPossible(self):
        return self.possible

    def getStudentID(self):
        return self._id

    @property
    def sourceobject(self):
        """
        A output compatible object for the source code to be put in the outputs list.

        :return: Object holding the students name and source code
        :rtype: qt.sourceformatting.SourceOutput
        """
        ret = SourceOutput()
        ret._name = self.name
        ret._output = self.source
        return ret

    @student.Student.state.setter
    def state(self, st):
        self._state = st
        self.status_nameChanged.emit(self)
        self.flagChanged.emit()

    @classmethod
    def getid(cls):
        """
        Generate a new unique student id for the life of the program

        :return: The generated id
        :rtype: int
        """
        cur = cls.lastid + 1 # Add one to the last id
        while cur in cls.allottedids:  # See if the id has already been assigned
            cur += 1  # Add one until we find one that hasn't been
        cls.allottedids.add(cur)  # Add it to the allotted ids
        cls.lastid = cur  # Change lastid
        return cur

    # Setup the QProperties
    studentName = QProperty(str, getName, setName, notify=nameChanged)
    status_name = QProperty(str, getStatus_name, notify=status_nameChanged)
    totalScore = QProperty(int, getScore, notify=scoreChanged)
    totalPossible = QProperty(int, getPossible, notify=possibleChanged)
    flag = QProperty(str, getFlag, notify=flagChanged)
    studentID = QProperty(int, getStudentID, notify=studentIDChanged)


class StudentQList(QAbstractListModel):
    """
    A data model for student objects.
    """
    #The available fields
    COL = (
        "studentObj", "studentName", "status_name", "totalScore", "totalPossible", "totalPossible", "flag", "studentID")

    def __init__(self, l, **kwargs):
        super(StudentQList, self).__init__(**kwargs)
        self.COL = dict(enumerate(StudentQList.COL))  # Number the fields and put them in a dict
        self.setRoleNames(self.COL)  # Set the fields as roles in the data model
        self._list = list(l)  # Set the given python list as our data source

    def rowCount(self, *args, **kwargs):
        """
        Get the number of rows we have
        :param args: Additional arguments
        :param kwargs: Additional named arguments
        :return: The number of rows in the model
        :rtype: int
        """
        return len(self._list)

    def data(self, index, role, *args, **kwargs):
        """
        Get a piece of data from the model
        :param index: An index object
        :param role: The desired role to retrieve
        :param args: Additional arguments
        :param kwargs: Additional named arguments
        :return: The requested data or None if not found
        """
        try:
            name = self.COL[role]  # Find the desired role
            if name == "studentObj":  # We're looking for the actual student object
                return self._list[index.row()]  # So return that
            return getattr(self._list[index.row()], name)  # Else look up the attribute and return that
        except:
            pass
        return None  # Return none if there we're any errors or if anything else occurred
