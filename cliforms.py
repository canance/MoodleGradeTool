__author__ = 'phillip'

import npyscreen
import curses
import locale
from testing import tests
import os.path
from os.path import abspath

theme = npyscreen.Themes.TransparentThemeLightText

class FileDialog(npyscreen.ActionForm):
    def __init__(self, folder="", conf=""):
        self.fpath = folder  # The default grading folder
        self.cpath = conf  # The default configuration folder
        npyscreen.Form.__init__(self)

    def create(self):
        self.name = "Select Files"

        self.invalid_dir = self.add(npyscreen.FixedText)
        self.invalid_conf = self.add(npyscreen.FixedText)

        self.nextrely +=2

        self.directory = self.add(npyscreen.TitleFilename, name="Folder/zip to grade (default: current directory): ")
        self.directory.value = self.fpath
        self.testconf = self.add(npyscreen.TitleFilename, name="Test configuration data (default: same as above): ")
        self.testconf.value = self.cpath

        self.set_editing(self.directory)



    def on_ok(self):
        path = self.directory.value
        conf = self.testconf.value
        reset = False

        if path and not os.path.exists(path):
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
            self.display()
            self.editing = True

    def on_cancel(self):
        self.directory.value = self.fpath
        self.testconf.value = self.cpath


class TestsSelector(npyscreen.Form):


    def create(self):
        self.name = "Test selection"
        tlist = tests.keys()

        self.selector = self.add(npyscreen.MultiSelect, name='Select Tests to automatically run: ', values=tlist,
                                 max_height=len(tlist))
        self.add(npyscreen.FixedText, name="", value="NOTE: You will have the option to run manual later")

class StudentRecord(npyscreen.SplitForm):

    def __init__(self, student=None, *args, **kwargs):
        self.student = student
        npyscreen.SplitForm.__init__(self, *args, **kwargs)

    def changedisplay(self):
        if len(self.seloutput.value) == 0:
            return
        val = self.seloutput.value[0]
        if val == 0:
            self.textdisplay.values = self.getsource()
            self.textdisplay.name = "Source: " + self.student.java_class
        else:
            val -= 1
            test = self.outputs[val]
            self.textdisplay.values = test.output().split('\n')
            self.textdisplay.name = test.name
        self.display()


    def create(self):
        self.name = "Test results for {student}".format(student=self.student.name)
        self.testresults = ["{test.name:<33}{test.score}/{test.possible}".format(test=test) for test
                            in self.student.tests]

        self.outputs = filter(lambda t: hasattr(t, 'output'), self.student.tests)
        outlist = ['Source'] + [out.name for out in self.outputs]

        self.textdisplay = self.add(npyscreen.TitlePager, name="Source: " + self.student.java_class,
                                    values=self.getsource(), max_height=self.get_half_way() - 2)

        self.nextrely = self.get_half_way() + 1

        select_height = (self.get_half_way() / 2) - 1
        self.add(npyscreen.TitleMultiLine, name="Test results",
                 max_height=select_height, max_width=55, values=self.testresults)
        tempx = self.nextrelx
        tempy = self.nextrely

        self.seloutput = self.add(npyscreen.TitleSelectOne, name="Display", values=outlist, max_height=select_height)

        self.nextrelx = tempx
        self.nextrely = tempy

        self.nextrelx = 60
        self.nextrely = self.get_half_way() + 1

        total = "Total score: {s.score}/{s.possible}".format(s=self.student)
        self.add(npyscreen.FixedText, name="", value=total, max_width=len(total))

        self.nextrely += 5

        self.checksave = self.add(npyscreen.RoundCheckBox, name="Save test output")
        self.checkmanual = self.add(npyscreen.RoundCheckBox, name="Do manual test")

        self.seloutput.when_value_edited = self.changedisplay



    def getsource(self):
        ret = ""
        sourcepath = abspath('./' +self.student.name + '/' + '/'.join(self.student.java_class.split('.')) + '.java')
        with open(sourcepath, 'r') as f:
            ret = [l.strip('\n') for l in f.readlines()]

        return ret

def break_forms(func):
    pass

def forms(func):

    def npyscreen_wrapper(*args, **kwargs):
        locale.setlocale(locale.LC_ALL, '')

        return curses.wrapper(setup, func, *args, **kwargs)

    return npyscreen_wrapper

def setup(stdscr, func,*args,**kwargs):
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