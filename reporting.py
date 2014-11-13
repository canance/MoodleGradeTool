__author__ = 'phillip'

from lxml import etree as ET
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import namedtuple

reporttypes = set()

FileTypes = namedtuple("FileTypes", ("name", "extensions"))


class Report(object):
    __metaclass__ = ABCMeta

    filetypes = FileTypes("Invalid", (".check", ".your", ".code"))

    def __init__(self, **kwargs):
        super(Report, self).__init__(**kwargs)


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
        if isinstance(fd, basestring):
            fd = open(fd, mode="w")
        fd.write(str(self))

    @classmethod
    def register(cls):
        reporttypes.add(cls)


class XMLReport(Report):

    filetypes = FileTypes("XML Grade Report", (".xml"))

    def __init__(self, studentlist, **kwargs):
        super(XMLReport, self).__init__(**kwargs)
        self.studentlist = studentlist

    def generate_report(self):
        """
        Generates an XML file from the list of students in studentlist.

        :return: An LXML etree representing the report
        """
        root = ET.Element("Results")
        for s in self.studentlist:
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
        students = source if not isinstance(source, XMLReport) else source.studentlist
        super(XSLReport, self).__init__(students, **kwargs)

    def generate_report(self):
        root = super(XSLReport, self).generate_report()
        path = "/".join(__file__.split("/")[:-1]) + "/reporting/XSL_FO Default.xml"
        transform = ET.XSLT(ET.parse(path))
        root = transform(root)
        return root

XSLReport.register()