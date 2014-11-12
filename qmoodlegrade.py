__author__ = 'phillip'

studentslist = None

import qt
import sys
from qt.qtdispatch import QTDispatcher
from PySide.QtCore import QThread

def main():
    qt.mainthread = QThread.currentThread()
    qt.initialize_view()
    dispatch_thread = QThread()
    qt.maindispatch = QTDispatcher(qt.mainview)
    qt.qapp.lastWindowClosed.connect(dispatch_thread.quit)
    qt.maindispatch.moveToThread(dispatch_thread)
    dispatch_thread.start()
    qt.mainview.show()
    res = qt.qapp.exec_()
    dispatch_thread.wait()
    sys.exit(res)

if __name__ == "__main__":
    main()
