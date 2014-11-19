"""The classes used to run the tests."""

from moodlegradetool import filemanager
from moodlegradetool.util import polyopen

__author__ = 'phillip'

import sys, os

import re
import subprocess
import abc
import datetime
import pexpect, fdpexpect
import StringIO
from lxml import etree
from collections import defaultdict
from functools import partial
import shutil

FileMapping = filemanager.FileMapping
testers = set()  #: The registered Testers

tests = {}  #: The available Tests


def findtests(path):
    """
    Locate test configuration files. Any suported files that are found have the corresponding class generated and
    added to tests, keyed to the name.

    :param path: The path to search
    """
    tests.clear()
    olddir = os.curdir
    os.chdir(path)
    for filename in os.listdir(path):
        if filename.endswith(".test") or filename.endswith(
                ".testx"):  # Find the files that end with .test in the grading dir
            with open(path + '/' + filename, 'r') as f:  # Open the file
                for tester in testers:
                    if tester.handlesconfig(f):  # And ask the testers if they handle that kind of file
                        tester.parse_config(path + '/' + filename)  # If they do, give them the file path to parse
                        break
                    else:
                        f.seek(0)  # Need to reset the file position for next check
    os.chdir(olddir)


def find_package(origfile, destfile, classname, path):
    classDeclaration = "public class " + classname
    package = None
    # Use context manager for handling file objects (no need to explicitly close the file) -Phillip Wall
    with open(origfile) as fHandle:
        for line in fHandle:
            if classDeclaration in line:
                break
            if "package " in line:
                #Strip trailing ';' with strip method -Phillip Wall
                package = line.replace("package ", "").strip(';\r\n')
                #1. create a new directory for the package
                #2. Move the class file to the package directory
                destdir = "{}/{}".format(path, package)

                if not os.path.exists(destdir):
                    os.mkdir(destdir)

                destfile = destdir + "/%s.java" % classname
                classname = package + "." + classname
                return destfile, classname, package
    return destfile, classname, package


class TesterMeta(abc.ABCMeta):
    """Metaclass for testers. This is what takes the dict returned by parse_config and generates the subclass"""
    def __init__(cls, clsname, bases, attr):
        super(TesterMeta, cls).__init__(clsname, bases, attr)



        parser = cls.parse_config  # Get the class's parse config_function

        @classmethod
        def load_config(clss, configfile):  # This will replace parse_config on the class
            """
            Parse the configuration and return a dict. The elements in the dict will added to the test class's dict.
            Tester handles making the dict elements available, subclassing for the particular test, and registering the
            test. A name key should be in the dict that has the tests name.

            .. note:: The returned dict will get intercepted, the apparent return value is None.

            :param configfile: The path of the configuration file to parse
            :return: Dictionary of attributes from the configuration file
            :rtype: dict
            """
            attrs = cls.__dict__.copy()  # Copy the class's dict
            attribd = parser(configfile)
            # Don't wrap parse config if we're doing tests
            if hasattr(TesterMeta, 'disable') and getattr(TesterMeta, 'disable'):
                return attribd
            attrs.update(attribd)  # Update the copy with the parsed config file
            name = attrs['name']  # Get the tests name
            tests[name] = type(name, (cls, ), attrs)  # Create the subclass for the test and register it

        cls.parse_config = load_config  # Replace the class's parse_config


class Tester(object):
    """Base class for testers. All tester classes should inherit from this.

    :cvar cwd: In a class context, a format string with student and clsName fields.
    :ivar cwd: In an instance context, cwd is formatted and made absolute. Holds the working directory for this test
    :ivar student: Holds the students name
    :ivar claName: Holds the name of the main class
    """
    __metaclass__ = TesterMeta

    cwd = './{student}'

    def __init__(self, student, clsName):
        self.student = student
        self.clsName = clsName
        self.cwd = os.path.abspath(self.cwd.format(student=student, cls=clsName))
        self._score = 0

    @abc.abstractmethod
    def start(self):
        """
        **Abstract:** Called to start the test
        """
        pass

    @classmethod
    def register(cls):
        """Registers the class with the main program. When registered this class will be asked if it supports
        any found configuration files."""
        testers.add(cls)

    @classmethod
    @abc.abstractmethod
    def parse_config(cls, configfile):
        """
        Parse the configuration and return a dict. The elements in the dict will added to the test class's dict.
        Tester handles making the dict elements available, subclassing for the particular test, and registering the
        test. A name key should be in the dict that has the tests name.

        .. note:: The returned dict will get intercepted, the apparent return value is None.

        :param configfile: The path of the configuration file to parse
        :return: Dictionary of attributes from the configuration file
        :rtype: dict
        """

        return {}

    @abc.abstractproperty
    def score(self):
        """
        The score the program got.

        :rtype: int
        """
        pass

    @abc.abstractproperty
    def possible(self):
        """
        The possible score on this test.

        :rtype: int
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def handlesconfig(fd):
        """
        Returns true if the config in the file object is handled by this Tester.

        :rtype : bool
        :param fd: A file object for the config file
        """
        return False

    def failed(self):
        return self.score() == self.possible()


class ManualTest(Tester):
    """Simple tester that allows for manual interaction with the program at the command line.
    The std* attributes can be modified to direct the java program's input and output."""

    stdin, stdout, sterr = sys.stdin, sys.stdout, sys.stderr

    @classmethod
    def parse_config(cls, configfile):
        return {'name': configfile}

    @property
    def score(self):
        return 1

    @property
    def possible(self):
        return 1

    def start(self):
        subprocess.call(('java', self.clsName), stdin=self.stdin, stdout=self.stdout, stderr=self.stderr, cwd=self.cwd)

    @staticmethod
    def handlesconfig(path):
        return False


class RegexTester(Tester):
    """A simple tester that can take an input file and feed it to the java program. It tests the output against a
    list of regexes. Each matched regex is worth on point. It has a simple configuration format.

    :ivar name: The tests name
    :ivar main: The class to test, if None uses the main class from the student
    :ivar regexs: The list of regexs to comapare the output to
    :ivar input_file: The file to pass to the java program
    """

    @classmethod
    def parse_config(cls, configfile):
        ret = {}
        ret['config_dir'] = os.getcwd()
        ret['cp'] = []
        ret['main'] = None

        detectors = (cls._detect_name, cls._detect_infile, cls._detect_regex, cls._detect_cp, cls._detect_main)
        with polyopen(configfile) as f:
            for line in f:
                line = line.strip()

                if line and line[0] == "#":
                    continue  # Skip comments
                for func in detectors:
                    if func(line, ret):
                        break

        return ret

    @classmethod
    def _detect_cp(cls, line, d):
        if line and line.strip()[:4] == "CP: ":
            line = line[3:]
            src, dst = line.split('|')
            src = os.path.abspath(src.strip())
            dst = dst.strip()
            d.setdefault('cp', []).append((src, dst))
            return True

    @classmethod
    def _detect_main(cls, line, d):
        if line and line.strip()[:6] == "MAIN: ":
            line = line[5:]
            line = os.path.abspath(line.strip())
            d['main'] = line
            return True

    @classmethod
    def _detect_name(cls, line, d):
        if line and line.strip()[:6] == "NAME: ":
            line = line[5:].strip()
            if not d.has_key('name'):
                d['name'] = line
                return True

    @classmethod
    def _detect_infile(cls, line, d):
        if line and line.strip()[:7] == "STDIN: ":
            line = line[6:].strip()
            if (not d.has_key('input_file')):
                d['input_file'] = os.path.abspath(line)
                return True

    @classmethod
    def _detect_regex(cls, line, d):
        if line and line[:7].upper() == "REGEX: ":
            line = line[6:].strip()
            d.setdefault('regexes', []).append(re.compile(line))
            return True

    def output(self):
        """
        The output from the java program.

        :returns: The output from the last run
        :raises: AttributeError if called before start has been called.
        :rtype: String
        """
        return self._output

    @property
    def score(self):
        return self._score


    def start(self):

        # handle file copying
        #start filemanager copy, get key
        keys = []
        for path in self.cp:
            src, dst = path
            dst = "%s/%s" % (self.cwd, dst)
            keys.append(filemanager.copy(src, dst))
            print "DEST = " + dst

        #if main class was specified copy it and compile.  Replace self.clsName with main class.
        if self.main is not None:
            src = self.main
            dst = "%s/%s" % (self.cwd, os.path.basename(self.main))
            keys.append(filemanager.copy(src, dst))

            #get classname
            clsname = os.path.basename(dst)
            clsname = clsname[:-5]

            #determine if we need to be in a package
            origfile = self.cwd + "/" + "/".join(self.clsName.split(".")) + ".java"
            final_dst, clsname, package = find_package(origfile, dst, clsname, self.cwd)
            if package:
                tmp = "{}.tmp".format(dst)
                with file(dst) as input:
                    with file(tmp, 'w') as output:
                        output.write("package {};".format(package))
                        for line in input:
                            output.write(line)
                shutil.copy(tmp, final_dst)


            #compile
            with open(self.cwd + "/build.log", 'a') as log:  # Open the log file
                #Log entry header
                log.write('\n\n' + str(datetime.datetime.now()) + '\n')
                log.write("Starting build of %s.java\n\n" % clsname)
                #Start the build
                proc = subprocess.Popen(('javac', "/".join(clsname.split(".")) + ".java"),
                                        cwd=self.cwd, stdout=log, stderr=subprocess.STDOUT)
                proc.wait()
            #set self.clsname to main class

            self.clsName = clsname

        self._score = 0

        #Call the java program with the input file set to stdin
        #Keep the output

        with polyopen(self.input_file) as f:
            try:
                self._output = subprocess.check_output(('java', self.clsName), stdin=f,
                                                       stderr=subprocess.STDOUT, cwd=self.cwd)
            except subprocess.CalledProcessError, e:
                self._output = e.output + "\n" + str(e)
                print "Program did not behave according to test information.  Please try running manually."
                print >> sys.stderr, e

        #Run all the detected regexes against the output
        self.report = []
        for reg in self.regexes:
            m = reg.search(self._output)
            if m:
                self._score += 1  # And count how many matches we got.

            self.report.append((reg.pattern, bool(m)))

        #clean up filemanager
        for key in keys:
            filemanager.clean(key)

    @staticmethod
    def handlesconfig(fd):
        return "#RegexTester" in fd.readline()

    @property
    def possible(self):
        return len(self.regexes)


class AdvancedRegexTester(Tester):
    """
    A more advanced regex tester. Pieces of data to be passed are included in the configuration file and regexes can
    include capture groups. The capture groups can then have further tests run on them to see if the program output
    the right value. Each matched regex is worth one point and each assertion is worth another point.

    :ivar name: The tests name
    :ivar qxpath: Partial function to perform xpath queries on the tree with the namespaces qualified
    :ivar regexs: The list of regexs used in the tests
    :ivar tree: The xml tree of the parsed file.
    """
    _score = 0

    @property
    def possible(self):
        return len(self.qxpath('//ar:assertion')) + len(self.qxpath('//ar:match'))

    def start(self):
        self.report = []
        main = None  # Placeholder for the main test
        others = []  # Holds other tests
        for test in self.tree.xpath('./ar:Test', namespaces={
            'ar': 'http://moodlegradetool.com/advanced_regex'}):  # Get all test nodes
            if (not 'file' in test.attrib) and not main:  # See if this is the first test with out a filename
                main = test  # Set it to be the main test
            else:
                others.append((test, test.get('file')))  # Append every other test to the others

        if not main: raise ValueError("Could not find the main test")

        java_cls = self.clsName if not hasattr(self, 'main') else self.main  # Get the main java class
        self._out = StringIO.StringIO()  # Make a stringIO to hold the output
        proc = pexpect.spawn('java', [java_cls], logfile=self._out, cwd=self.cwd)  # Spawn the java program

        self.do_test(proc, main)  # Do the main test

        for test, fname in others:  # Do the other tests
            with open(self.cwd + '/' + fname, 'r') as f:  # Open the associated file
                fexp = fdpexpect.fdspawn(f)  # Spawn an expect instance for the file
                self.do_test(fexp, test)  # Do the test

    def do_test(self, proc, testroot):
        # assert isinstance(testroot, etree.ElementBase)  # Make sure passed testroot is an element
        asserts = {}  # Dict for storing matches used in asserts
        qxpath = partial(testroot.xpath, namespaces={'ar': 'http://moodlegradetool.com/advanced_regex'})
        for exp in qxpath('./ar:Expect'):  # For every Expect node in testroot
            prmt = False
            try:
                if 'prompt' in exp.attrib:  # See if we're expecting a prompt
                    proc.expect(exp.get('prompt'))  # Get and use the prompt
                    prmt = True  # Set this to true so we send a new line later
                else:
                    proc.expect(pexpect.EOF)  # Else wait until end of file
            except pexpect.TIMEOUT:
                break
            out = proc.before  #+ proc.after  # Get everything before and up to the match
            for ele in exp:  # For every element int the expect node
                if ele.tag == "{http://moodlegradetool.com/advanced_regex}match":  # If its a match tag find the regex
                    expr = self.regexes[ele.text]  # Get the regex
                    m = expr.search(out)  # Try to do a match
                    if m: self._score += 1  # If there is one raise the score
                    if 'id' in ele.attrib:  # If this match has an id
                        asserts[str(ele.get('id'))] = m  # Store it for later
                    self.report.append(("MATCH: " + expr.pattern, bool(m)))
                if ele.tag == "{http://moodlegradetool.com/advanced_regex}input":  # If its an input tag
                    txt = ele.text.strip()
                    #Try to find the input
                    if txt in self.inputs:
                        proc.send(self.inputs[txt] + ' ')  # Send a normal input followed by a space
                    elif txt in self.files:
                        fname = self.files[txt].destination  # If its a file input
                        proc.send(fname + ' ')  # Send the destination file name
            if prmt:
                proc.sendline('')  # If this was a prompt send a new line

        for assr in qxpath('./ar:assertion'):  # For every assert tag in the test root
            m = asserts.get(str(assr.get('match')), None)  # Get the corresponding match object
            if not m:
                self.report.append(("ASSERT: " + assr.get('match') + " - No Match", False))
                continue  # If there was no match continue

            passes = True
            for grp in assr:  # Get all the match groups
                id = grp.get('id')  # Get the group id
                try:
                    id = int(id)  # Attempt to cast it to an int
                except ValueError:
                    pass

                txt = grp.text.strip()  # Strip the match text
                passes = passes and (m.group(id).strip() == txt)  # See if there is a match
                if not passes:
                    break  # If we're not passing this assert break

            if passes: self._score += 1  # If the assert passed increase the score
            self.report.append(("ASSERT: " + assr.get('match'), passes))

    @staticmethod
    def handlesconfig(fd):
        count = 0
        for l in fd:
            if "<AdvRegexTester" in l:
                return True
            elif count > 5:
                return False
            count += 1
        return False

    @classmethod
    def parse_config(cls, configfile):
        config = etree.parse(configfile).getroot()
        qxpath = partial(config.xpath, namespaces={'ar': "http://moodlegradetool.com/advanced_regex"})
        ret = {}

        ret['qxpath'] = qxpath
        ret['name'] = qxpath('./ar:name/text()')[0].strip()
        main = qxpath('./ar:main/text()')
        if main:
            ret['main'] = main[0].strip()

        regexes = {}
        for ele in qxpath("./ar:Definitions/ar:Regex"):
            regexes[ele.attrib['id']] = re.compile(ele.text)
        ret['regexes'] = regexes
        inputs = {}
        for ele in qxpath("./ar:Definitions/ar:input"):
            inputs[ele.attrib['id']] = ele.text.strip()
        ret['inputs'] = inputs
        ret['files'] = defaultdict(list)

        for ele in qxpath("./ar:Definitions/ar:file"):
            id = 'Default' if not 'id' in ele.attrib else ele.attrib['id']
            ret['files'][id].append(FileMapping(*[s.strip() for s in ele.text.split(':')]))

        ret['tree'] = config
        return ret

    def output(self):
        return self._out.getvalue()

    @property
    def score(self):
        return self._score


ManualTest.parse_config('Manual')

RegexTester.register()

AdvancedRegexTester.register()
