"""Contains classes for making reports from the students list."""

__author__ = 'phillip'

from lxml import etree as ET
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import namedtuple

reporttypes = set()

FileTypes = namedtuple("FileTypes", ("name", "extensions"))
#FileTypes.__doc__ = """Structure for the file types the report supports
#                        :ivar name: The name of the file type
#                        :ivar extensions: A list of file extensions (the first one is the default)"""


class Report(object):
    """Abstract: Base reporting class"""
    __metaclass__ = ABCMeta

    filetypes = FileTypes("Invalid", (".check", ".your", ".code"))

    def __init__(self, source, **kwargs):
        super(Report, self).__init__(**kwargs)
        self.source = source

    @abstractmethod
    def generate_report(self):
        """
        Abstract Method: Parse the given source and return a raw report. This could usually be a string, but depends
        on the report type.

        :return: Raw report object
        """
        pass

    def __str__(self):
        return str(self.generate_report())

    def save(self, fd):
        """Writes this report to the given file.

        :param fd: A file name or file-like object"""
        if isinstance(fd, basestring):
            with open(fd, mode="w") as f:
                f.write(str(self))
        else:
            fd.write(str(self))

    @classmethod
    def register(cls):
        """
        Registers this report type with the reports list.
        """
        reporttypes.add(cls)


class XMLReport(Report):
    """Makes an xml report from the students."""

    filetypes = FileTypes("XML Grade Report", (".xml", ))

    def __init__(self, source, **kwargs):
        super(XMLReport, self).__init__(**kwargs)

    def generate_report(self):
        """
        Generates an XML file from the list of students in source.

        :return: An LXML etree representing the report
        :rtype: lxml.etree._ElementTree
        """
        root = ET.Element("Results")
        for s in self.source:
            student = ET.SubElement(root, "student", {"name": s.name})
            for t in s.tests:
                test = ET.SubElement(student, "test", {"score": str(t.score), "possible": str(t.possible), "name": t.name})
                if hasattr(t, "report"):
                    for name, passed in t.report:
                        ET.SubElement(test, "part", {"name": name, "passed": str(passed)})

        return root.getroottree()

    def save(self, fd):
        self.generate_report().write(fd, pretty_print=True)

    def __str__(self):
        return ET.tostring(self.generate_report(), pretty_print=True)

XMLReport.register()


class XSLReport(XMLReport):

    filetypes = FileTypes("Raw XSL-FO file", (".fo", "xsl", ".xsl-fo", ".xml"))

    def __init__(self, source, **kwargs):
        super(XSLReport, self).__init__(source, **kwargs)

    def generate_report(self):
        root = super(XSLReport, self).generate_report()
        path = "/".join(__file__.split("/")[:-1]) + "/reporting/XSL_FO Default.xml"
        transform = ET.XSLT(ET.parse(path))
        root = transform(root)
        return root

XSLReport.register()
