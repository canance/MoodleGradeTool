"""Contains classes for making reports from the students list."""

__author__ = 'phillip'

from lxml import etree as ET

class XMLReport(object):

    def __init__(self, studentlist, **kwargs):
        super(XMLReport, self).__init__(**kwargs)
        self.studentlist = studentlist

    def generate_report(self):
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

class XSLReport(XMLReport):

    def __init__(self, source, **kwargs):
        students = source if not isinstance(source, XMLReport) else source.studentlist
        super(XSLReport, self).__init__(students, **kwargs)


    def generate_report(self):
        root = super(XSLReport, self).generate_report()
        path = "/".join(__file__.split("/")[:-1]) + "/reporting/XSL_FO Default.xml"
        transform = ET.XSLT(ET.parse(path))
        root = transform(root)
        return root