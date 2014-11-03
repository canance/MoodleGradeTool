__author__ = 'phillip'

import sys,os

import re
import subprocess
import abc
import filemanager
import datetime
import shutil


testers = set()  # The available test types

tests = {}  # The available tests

def findtests(path):
    tests.clear()
    olddir = os.curdir
    os.chdir(path)
    for filename in os.listdir(path):
        if filename.endswith(".test"):  # Find the files that end with .test in the grading dir
            with open(path + '/' + filename, 'r') as f:  # Open the file
                for tester in testers:
                    if tester.handlesconfig(f):  # And ask the testers if they handle that kind of file
                        tester.parse_config(path+ '/' + filename)  # If they do, give them the file path to parse
                        break
                    else:
                        f.seek(0)  # Need to reset the file position for next check
    os.chdir(olddir)



def find_package(origfile, destfile, classname, path):
    classDeclaration = "public class " + classname
    package = None
    #Use context manager for handling file objects (no need to explicitly close the file) -Phillip Wall
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

    def __init__(cls, clsname, bases, attr):
        super(TesterMeta, cls).__init__(clsname, bases, attr)

        parser = cls.parse_config # Get the classes parse config_function

        @classmethod
        def load_config(clss, configfile):  # This will replace parse_config on the class
            attrs = cls.__dict__.copy()  # Copy the class's dict
            attrs.update(parser(configfile))  # Update the copy with the parsed config file
            name = attrs['name']  # Get the tests name
            tests[name] = type(name, (cls, ), attrs)  # Create the subclass for the test and register it

        cls.parse_config = load_config  # Replace the class's parse_config


class Tester(object):
    __metaclass__ = TesterMeta

    cwd = './{student}'

    def __init__(self, student, clsName):
        self.student = student
        self.clsName = clsName
        self.cwd = os.path.abspath(self.cwd.format(student=student, cls=clsName))
        self._score = 0

    @abc.abstractmethod
    def start(self):
        pass

    @classmethod
    def register(cls):
        """Registers the class with the main program. When registered this class will be asked if it supports
        any found configuration files."""
        testers.add(cls)

    @classmethod
    @abc.abstractmethod
    def parse_config(cls, configfile):
        """Parse the configuration and return a dict. The elements in the dict will added to the test class's dict.
        Tester handles making the dict elements available, subclassing for the particular test, and registering the
        test. A name key should be in the dict that has the tests name.

        :param configfile: The path of the configuration file to parse
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
        subprocess.call(('java', self.clsName), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, cwd=self.cwd)

    @staticmethod
    def handlesconfig(path):
        return False

class RegexTester(Tester):

    @classmethod
    def parse_config(cls, configfile):
        ret = {}
        ret['config_dir'] = os.getcwd()
        ret['cp'] = []
        ret['main'] = None

        detectors = (cls._detect_name, cls._detect_infile,  cls._detect_regex, cls._detect_cp, cls._detect_main)
        with open(configfile) as f:
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
        if line and line[:4] == "CP: ":
            line = line[3:]
            src, dst = line.split('|')
            src = os.path.abspath(src.strip())
            dst = dst.strip()
            d.setdefault('cp', []).append((src, dst))
            return True

    @classmethod
    def _detect_main(cls, line, d):
        if line and line[:6] == "MAIN: ":
            line = line[5:]
            line = os.path.abspath(line.strip())
            d['main'] = line
            return True

    @classmethod
    def _detect_name(cls, line, d):
        if line and line[:6] == "NAME: ":
            line = line[5:].strip()
            if not d.has_key('name'):
                d['name'] = line
                return True

    @classmethod
    def _detect_infile(cls, line, d):
        if line and line[:7] == "STDIN: ":
            line = line[6:].strip()
            if (not d.has_key('input_file')) and os.path.isfile(line):
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
        :returns: The output from the last run
        :raises: AttributeError if called before start has been called.
        :rtype: String
        """
        return self._output

    @property
    def score(self):
        return self._score


    def start(self):

        #handle file copying
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

        with open(self.input_file) as f:
            try:
                self._output = subprocess.check_output(('java', self.clsName), stdin=f,
                                                   stderr=subprocess.STDOUT, cwd=self.cwd)
            except subprocess.CalledProcessError, e:
                self._output = e.output + "\n" + str(e)
                print "Program did not behave according to test information.  Please try running manually."
                print >> sys.stderr, e

        #Run all the detected regexes against the output
        for reg in self.regexes:
            m = reg.search(self._output)
            if m:
                self._score += 1  # And count how many matches we got.

        #clean up filemanager
        for key in keys:
            filemanager.clean(key)

    @staticmethod
    def handlesconfig(fd):
        return "RegexTester" in fd.readline()

    @property
    def possible(self):
        return len(self.regexes)


ManualTest.parse_config('Manual')

RegexTester.register()