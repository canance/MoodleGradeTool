__author__ = 'phillip'

import npyscreen
import curses
import locale
from testing import tests
import os.path
from os.path import abspath

theme = npyscreen.Themes.TransparentThemeLightText

class FileDialog(npyscreen.ActionForm):
    """
    The form that collects the folders to work with.
    """
    def __init__(self, folder="", conf=""):
        self.fpath = folder  # The default grading folder
        self.cpath = conf  # The default configuration folder
        npyscreen.Form.__init__(self)

    def create(self):
        self.name = "Select Files"

        #These will display messages for when the user provides invalid paths
        self.invalid_dir = self.add(npyscreen.FixedText)
        self.invalid_conf = self.add(npyscreen.FixedText)

        #Move down two lines
        self.nextrely += 2

        #Get the paths and set them to the default values
        self.directory = self.add(npyscreen.TitleFilename, name="Folder/zip to grade (default: current directory): ")
        self.directory.value = self.fpath
        self.testconf = self.add(npyscreen.TitleFilename, name="Test configuration data (default: same as above): ")
        self.testconf.value = self.cpath

        #Set the widget that were currently editing to the one for the main directory
        self.set_editing(self.directory)

    def on_ok(self):

        #Get values for local access (faster and easier)
        path = self.directory.value
        conf = self.testconf.value
        reset = False  # For when we need to continue editing

        if path and not os.path.exists(path):
            #Display a message on the form
            self.invalid_dir.value = "Incorrect path for directory to grade"
            reset = True
        else:
            self.invalid_dir.value = ""

        if conf and not os.path.exists(conf):
            self.invalid_conf.value = "Incorrect path for test configuration data"
            reset = True
        else:
            self.invalid_conf.value = ""

        if reset:
            self.display()  # Refresh the screen
            self.editing = True  # And set editing back to true so the form knows we need to stay

    def on_cancel(self):
        #Reset to what was passed in
        self.directory.value = self.fpath
        self.testconf.value = self.cpath


class TestsSelector(npyscreen.Form):
    """
    Displays a list of tests to select from.
    """
    def create(self):
        self.name = "Test selection"
        tlist = tests.keys()
        ltlist = len(tlist)

        self.selector = self.add(npyscreen.MultiSelect, name='Select Tests to automatically run: ', values=tlist,
                                 max_height=ltlist if ltlist > 1 else 2)
        self.add(npyscreen.FixedText, name="", value="NOTE: You will have the option to run manual later")


class StudentRecord(npyscreen.SplitForm):
    """
    Displays the current status of a student object
    """
    def __init__(self, student=None, *args, **kwargs):
        self.student = student  # Store the student object
        npyscreen.SplitForm.__init__(self, *args, **kwargs)

    def changedisplay(self):
        """This is run when a new output is selected."""
        if len(self.seloutput.value) == 0:
            return  # If nothing is selected in the list leave things as they are
        val = self.seloutput.value[0]  # Get the first value selected (there should only be one
        if val == 0:  # If its zero
            self.textdisplay.values = self.getsource() # We want to show the source code
            self.textdisplay.name = "Source: " + self.student.java_class
        else:
            val -= 1  # Otherwise we decrease the value by one
            test = self.outputs[val]  # Get the test's output we want to display
            self.textdisplay.values = test.output().split('\n')  # Split on new lines and display it
            self.textdisplay.name = test.name
        self.display()  # Update the display


    def create(self):
        self.name = "Test results for {student}".format(student=self.student.name)  # Set the name of the form
        #Get the results for each test
        self.testresults = ["{test.name:<33}{test.score}/{test.possible}".format(test=test) for test
                            in self.student.tests]

        #Get all the tests in the student tests list that have an output attribute
        self.outputs = filter(lambda t: hasattr(t, 'output'), self.student.tests)

        #Make a list of all the avaiable things to display
        outlist = ['Source'] + [out.name for out in self.outputs]

        #The main text display, we set the maximum height of this widget to the half way point minus 2
        self.textdisplay = self.add(npyscreen.TitlePager, name="Source: " + self.student.java_class,
                                    values=self.getsource(), max_height=self.get_half_way() - 2)

        #Go below the line
        self.nextrely = self.get_half_way() + 1

        #Figure out the height needed for the two select boxes
        select_height = (self.get_half_way() / 2) - 1
        self.add(npyscreen.TitleMultiLine, name="Test results",  # This shows the test results
                 max_height=select_height, max_width=55, values=self.testresults)

        #print select_height
        self.seloutput = self.add(npyscreen.TitleSelectOne, name="Display", values=outlist, max_height=select_height)

        #Start second column
        self.nextrelx = 60
        self.nextrely = self.get_half_way() + 1

        #Displayes the total score of the student
        total = "Total score: {s.score}/{s.possible}".format(s=self.student)

        self.add(npyscreen.FixedText, name="", value=total, max_width=len(total))

        self.nextrely += 5  # Skip 5 rows

        #Add the check boxes for other things to do once the test is done
        self.checksave = self.add(npyscreen.RoundCheckBox, name="Save test output")
        self.checkmanual = self.add(npyscreen.RoundCheckBox, name="Do manual test")

        #Set up the changedisplay function to handle when the output selection widget's value has changed
        self.seloutput.when_value_edited = self.changedisplay

    def getsource(self):
        """Gets the source code of the main class"""
        ret = ""
        sourcepath = abspath('./' +self.student.name + '/' + '/'.join(self.student.java_class.split('.')) + '.java')
        with open(sourcepath, 'r') as f:
            ret = [l.strip('\n') for l in f.readlines()]  # Gets the lines in the source file and strips the new lines

        return ret


def break_forms(func):
    pass


def forms(func):
    """
    Decorator: Sets up curses for the function it decorates. Uses the curses wrapper function as a backend
    """
    def npyscreen_wrapper(*args, **kwargs):
        locale.setlocale(locale.LC_ALL, '')

        return curses.wrapper(setup, func, *args, **kwargs)

    return npyscreen_wrapper


def setup(stdscr, func,*args,**kwargs):
    """Used to set the npyscreen theme"""
    npyscreen.setTheme(theme)
    return func(stdscr, *args, **kwargs)


def break_curses(func, *args, **kwargs):
    #Tear down curses
    stdscr.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
    ret = func(*args, **kwargs)
    # Initialize curses
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    try:
        curses.start_color()
    except:
        pass

    return ret