# #########################################################################
# Author:      Cory Nance
# Author:      Phillip Wall
# Description: Script to grade labs   									 
# Date: 	   20 August 2014											 
# Assumptions: Submissions were mass-downloaded from Moodle and unzipped.
##########################################################################

import cliforms

import os
import sys
import shutil

import zipfile
import re
import student
import argparse

from testing import tests, testers

from threading import Thread
from Queue import Queue

MAX_BUILDS = 5

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # Force unbuffered stdout

def main():

    parser = argparse.ArgumentParser(description="Compile, test, and grade Java files submitted via Moodle.")
    parser.add_argument('-p', '--path', metavar='FolderPath', type=str, help='Path to a zip file or folder containing the Moodle submissions.')
    parser.add_argument('-c', '--config', metavar='ConfigPath', type=str, help='Path to the configuration directory.')
    args = parser.parse_args()

    #set path and config variables
    path = os.path.abspath(args.path) if args.path else ""

    while not os.path.exists(path):
        if path != "":
            sys.stderr.write('Invalid path: ' + path + "\n")
        path = raw_input("Please enter a valid path: ")
        path = os.path.abspath(path)

    config = os.path.abspath(args.config) if args.config else ""

    if not os.path.exists(config):
        config = path

    paths = {'folder': path, 'config': config}

    # Fixed comparison to leverage negative indexes -Phillip Wall
    if '.zip' == path[-4:]:
        os.mkdir(path[:-4])

        with zipfile.ZipFile(path) as z:
            z.extractall(path=path[:-4])  # Extract the files

        path = path[:-4]  # Set path to newly created directory

    os.chdir(paths['config'])  # Change the working directory to the test configuration directory

    for filename in os.listdir(paths['config']):
        if filename.endswith(".test"):  # Find the files that end with .test in the grading dir
            with open(filename, 'r') as f:  # Open the file
                for tester in testers:
                    if tester.handlesconfig(f):  # And ask the testers if they handle that kind of file
                        tester.parse_config(filename)  # If they do, give them the file path to parse
                        break
                    else:
                        f.seek(0)  # Need to reset the file position for next check

    os.chdir(paths['folder'])

    tkeys = select_test()

    if tkeys:
        tlist = [tests[key] for key in tkeys]
    else:
        tlist = tests['Manual']

    print tlist
    student.Student.tests = tlist

    students = prepare_directory(path)  # Prepare the grading directory

    q = Queue(maxsize=MAX_BUILDS)  # Set up the build queue

    t = Thread(target=do_builds, args=(path, students, q))  # Set up the building thread

    t.start()

    #Keep going while the thread is alive or while there are still programs to be worked
    while t.isAlive() or not q.empty():

        #Get the information about the next program in the list
        currentstudent = q.get()
        assert isinstance(currentstudent, student.Student)

        #Print out the information
        print "#" * 35, '\n'
        print currentstudent.name
        print "{path}/{student}/{cls}.java".format(path=path, student=currentstudent.name,
                                                   cls=currentstudent.java_class)

        if currentstudent.state == student.StudentState.building:
            print "Waiting for build to finish..."
            currentstudent.proc.wait()

        if currentstudent.state == student.StudentState.build_error:
            print "There was a problem during build, check the build.log in the students folder."
            continue

        #Change the working path to the student's directory
        wrkpath = "{}/{}".format(path, currentstudent.name)

        #os.chdir(wrkpath)

        #NOTE The structure of this block will probably change significantly once pynscreen is done
        possible = 0

        print "Running tests..."
        currentstudent.dotests()
        for test in currentstudent.tests:
            possible += test.possible
            print "\nThe program got a score of {score}/{possible} on {test}".format(score=test.score,
                                                                                     possible=test.possible,
                                                                                     test=test.name)

        print "Program got a total score of {score}/{possible}".format(score=currentstudent.score,
                                                                       possible=possible)
        save, manual = process_tests(currentstudent)

        if save:
            for test in filter(lambda t: hasattr(t,'output'), currentstudent.tests):
                with open("{path}/{test}_output.log".format(path=wrkpath, test=test.name), 'w') as log:
                    log.write(test.output())

        if manual:
            ans = 'y'
            while ans and ans.lower()[0] == 'y':  # Continue while the user keeps pressing yes
                print
                currentstudent.dotest(tests['Manual'])
                ans = raw_input("Program finished, do you want to rerun it? (y/n)")
                print

    os.chdir(path)
    t.join()




#end main

@cliforms.forms
def fileconfig(*args):
    f = cliforms.FileDialog()
    f.edit()

    ret = {'folder': f.directory.value, 'config': f.testconf.value}

    if not ret['folder']:
        ret['folder'] = os.curdir

    if not ret['config']:
        ret['config'] = ret['folder']

    return ret

@cliforms.forms
def select_test(*args):
    """Will prompt the user for the test they want to run.
    :returns: A list of keys of the selected tests or None if none selected
    :rtype : List
    """

    keys = tests.keys()
    f = cliforms.TestsSelector()
    f.edit()
    indexes = f.selector.value

    if not indexes:
        return None

    return [keys[i] for i in indexes]

@cliforms.forms
def process_tests(stdscr, student):
    """
    Processes the results of a test.
    :returns: A tuple of (Save output, Run Manual)
    :rtype: tuple
    """
    f = cliforms.StudentRecord(student=student)
    f.edit()

    return f.checksave.value, f.checkmanual.value

def print_numbered(l):
    for i in xrange(len(l)):
        print str(i+1) + ". " + str(l[i])


def do_builds(path, studentslist, que):
    for curstudent in studentslist:
        curstudent.dobuild()
        que.put(curstudent)


def prepare_directory(path):
    """
    Prepares the grading directory by parsing the downloaded class files, separating them into student folders, and
    moving the java files to the corresponding directories.
    Returns a dict with the students name as the key, and list of java classes as the value.

    :param path: The directory to prepare
    :rtype : Dict
    """

    tmp = {}

    files = os.listdir(path)

    # Following regex will match strings in the format of "Student Name_assignsubmission_file_ClassName.java"
    # It will extract the student name and class name using capture groups
    # We compile it here to save time in the loop -Phillip Wall
    regex = re.compile(r"""
        (           #Start of first Capture group
            [^_]+   #Matches everything until the first underscore
        )
        _[^e]+e_    #Consumes everything after the underscore until it gets to e and then consumes e_
        (           #Start of second capture group
            [^.]+   #Matches everything until a period
        )""", re.VERBOSE)

    for f in files:

        #ignore dot files.
        #Fixed: unnecessary slicing operation -Phillip Wall
        if '.' == f[0]:
            continue


        # Moodle renames all submissions so they cannot be compiled as is. Luckily
        # it does include the original filename so we can paritition the string
        # and extract the original filename from it.  From there we can cp the file
        # in order to compile and run.

        m = regex.search(f)  #Attempt to match the filename

        if not m:
            continue  #If there is not a match this filename does not match the expected format, skip it.


        studentname = m.group(1)  #Get the student name from the match
        className = m.group(2)  #Get the className from the match
        destFile = "{}/{}/{}.java".format(path, studentname, className)
        origFile = "{}/{}".format(path, f)

        studentdir = "{}/{}".format(path, studentname)
        if not os.path.exists(studentdir):
            os.mkdir(studentdir)

        classDeclaration = "public class " + className

        #Use context manager for handling file objects (no need to explicitly close the file) -Phillip Wall
        with open(origFile) as fHandle:
            for line in fHandle:
                if classDeclaration in line:
                    break
                if "package " in line:
                    #Strip trailing ';' with strip method -Phillip Wall
                    package = line.replace("package ", "").strip(';\r\n')
                    #1. create a new directory for the package
                    #2. Move the class file to the package directory
                    destdir = "{}/{}/{}".format(path, studentname, package)

                    if not os.path.exists(destdir):
                        os.mkdir(destdir)

                    destFile = destdir + "/%s.java" % className

                    className = package + "." + className

        shutil.copy(origFile, destFile) #Copy the java file to the destination

        #Gets the class list for the student, if the student hasn't been added creates an empty list
        #Doing it this way allows for multifile java projects
        tmp.setdefault(studentname, []).append(className)

    res = []
    for name, cl in tmp.iteritems():
        main = cl.pop(0)  # Assume first class is the main one
        res.append(student.Student(name, main, cl))

    return res


if __name__ == "__main__":
    main()
#end if
