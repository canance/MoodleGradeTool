__author__ = 'phillip'

from pygments import highlight
from pygments.lexers.jvm import JavaLexer
from pygments.formatters.html import HtmlFormatter
from PySide.QtCore import QObject, Signal, Property as QProperty

class SourceOutput(QObject):
    """Adapter to put the source code in to the outputs list"""
    _name = ""  # Output's name
    _output = ""  # The output

    srcOutput = Signal()  # Needed to be usable in QML

    def __init__(self, **kwargs):
        #Initalize the QObject or there will be children crying, hair pulling, and gnashing of teeth if you forget
        super(SourceOutput, self).__init__(**kwargs)
        self.formatted = False

    def getName(self):
        """
        Returns the name of the output
        :rtype: str
        """
        return self._name

    def getOutput(self):
        """
        Returns the output
        :rtype: str
        """
        if not self.formatted:
            lex = JavaLexer()
            formatter = HtmlFormatter(full=True)
            formatter.noclasses = True
            self._output = highlight(self._output, lex, formatter)
            self.formatted = True
        return self._output

    #Make the QProperties
    name = QProperty(str, getName, notify=srcOutput)
    output = QProperty(str, getOutput, notify=srcOutput)