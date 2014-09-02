__author__ = 'phillip'

import npyscreen
import curses
import locale
from testing import tests
from os.path import abspath

theme = npyscreen.Themes.TransparentThemeLightText


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
        super(self, StudentRecord).__init__(*args, **kwargs)

    def changedisplay(self):

        val = self.seloutput.value[0]
        if val == 0:
            self.textdisplay.values = self.getsource()
        else:
            val -= 1
            self.textdisplay.values = self.outputs[val].output()


    def create(self):
        self.name = "Test results for {student}".format(student=self.student.name)
        self.testresults = ["{test.name:<33}{test.score}/{test.possible}".format(test=test) for test
                            in self.student.tests]

        self.outputs = filter(lambda t: hasattr(t, 'output'), self.student.tests)
        outlist = ['Source'] + [out.name for out in self.outputs]

        select_height = (self.get_half_way() / 2) - 1
        self.add(npyscreen.MultiLine, max_height=select_height, max_width=41, values=self.testresults)
        tempx = self.nextrelx
        tempy = self.nextrely

        self.nextrelx = 45
        self.nextrely = 3

        total = "Total score: {s.score}/{s.possible}".format(s=self.student)
        self.add(npyscreen.FixedText, name="", value=total, max_width=len(total))

        self.nextrelx = tempx
        self.nextrely = tempy

        self.seloutput = self.add(npyscreen.SelectOne, name="Display", values=outlist, max_height=select_height)

        self.nextrely = self.get_half_way() + 1

        self.textdisplay = self.add(npyscreen.TitlePager, name="Source: " + self.student.java_class,
                                    values=self.getsource())

        self.seloutput.when_value_edited = self.changedisplay

    def getsource(self):
        ret = ""
        sourcepath = abspath('./'+self.student.name+'/'.join(self.student.java_class.split('.'))+'.java')
        with open(sourcepath, 'r') as f:
            ret = f.readall()

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