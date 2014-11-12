__author__ = 'phillip'

studentslist = None

import qt
import sys
from qt.qtdispatch import QTDispatcher
from PySide.QtCore import QThread

def main():
    qt.mainthread = QThread.currentThread()
    startview()
    while qt.mainview.rootObject() is None:
        pass
    dispatch_thread = disthread()
    dispatch_thread.start()
    #start_dispatcher()
    qt.mainview.show()
    res = qt.qapp.exec_()
    dispatch_thread.wait()
    sys.exit(res)


def startview():
    qt.initialize_view()

def start_dispatcher():
    qt.maindispatch = QTDispatcher(qt.mainview)
    cur = QThread.currentThread()
    if not (qt.mainthread is None or cur is qt.mainthread):
        #qt.qapp.lastWindowClosed.connect(cur.quit())
        cur.exec_()

class disthread(QThread):

    def __init__(self, **kwargs):
        super(disthread, self).__init__(**kwargs)

    def run(self, *args, **kwargs):
        start_dispatcher()

if __name__ == "__main__":
    main()
