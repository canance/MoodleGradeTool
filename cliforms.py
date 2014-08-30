__author__ = 'phillip'

import npyscreen
import curses
import locale
from testing import tests

class TestsSelector(npyscreen.Form):


    def create(self):

        self.selector = self.add(npyscreen.SelectOne, name='Select Test: ', values=tests.keys())


def forms(func):

    def npyscreen_wrapper(*args, **kwargs):
        locale.setlocale(locale.LC_ALL, '')
        return curses.wrapper(func, *args, **kwargs)

    return npyscreen_wrapper