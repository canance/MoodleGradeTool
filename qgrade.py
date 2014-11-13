__author__ = 'phillip'

studentslist = None

import sys

from PySide.QtCore import QThread

import moodlegradetool.qt as qt
from moodlegradetool.qt.qtdispatch import QTDispatcher


def main():
    qt.mainthread = QThread.currentThread()  # Store current thread
    qt.initialize_view()  # Get the view ready
    dispatch_thread = QThread()  # The QThread to put the dispatcher on
    qt.maindispatch = QTDispatcher(qt.mainview)  # Set up the dispatcher
    qt.qapp.lastWindowClosed.connect(dispatch_thread.quit)  # Connect the close signal to the thread quit signal
    qt.maindispatch.moveToThread(dispatch_thread)  # Move the dispatcher to the new thread
    dispatch_thread.start()  # Start the thread
    qt.mainview.show()  # Show the main window
    res = qt.qapp.exec_()  # Start the event loop, exits when the last window has been closed
    dispatch_thread.wait()  # Wait for the dispatcher thread to finish
    sys.exit(res)

if __name__ == "__main__":
    main()
