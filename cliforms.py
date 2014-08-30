__author__ = 'phillip'

import npyscreen
import curses
import locale
from testing import tests

theme = npyscreen.Themes.TransparentThemeLightText


class TestsSelector(npyscreen.Form):


    def create(self):
        self.name = "Test selection"
        self.selector = self.add(npyscreen.SelectOne, name='Select Test: ', values=tests.keys())

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