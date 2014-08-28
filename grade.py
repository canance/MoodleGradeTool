# #########################################################################
# Author:      Cory Nance												 
# Description: Script to grade labs   									 
# Date: 	   20 August 2014											 
# Assumptions: Submissions were mass-downloaded from Moodle and unzipped.
##########################################################################

import os
import sys
import shutil

import subprocess
import zipfile
import re
import datetime
from testing import tests, testers

from threading import Thread
from Queue import Queue

MAX_BUILDS = 5

def main():
    if len(sys.argv) < 2:
        path = raw_input("Please enter the path (zip/folder): ")
    else:
        path = str(sys.argv[1])
    #end if


    path = os.path.abspath(path)  # Convert the path to an absolute path

    # Fixed comparison to leverage negative indexes -Phillip Wall
    if '.zip' == path[-4:]:
        os.mkdir(path[:-4])

        with zipfile.ZipFile(path) as z:
            z.extractall(path=path[:-4])  # Extract the files

        path = path[:-4]  # Set path to newly created directory

    os.chdir(path)

    for file in os.listdir(path):
        if file.endswith(".test"):
            with open(path + '/' + file, 'r') as f:
                for tester in testers:
                    if tester.handlesconfig(f):
                        tester.parse_config(path+'/'+file)
                        break

    students = prepare_directory(path)

    q = Queue(maxsize=MAX_BUILDS)

    t = Thread(target=do_builds, args=(path, students.iteritems(), q))

    t.start()

    while t.isAlive() or not q.empty():

        studentName, className, buildProc = q.get()

        print "#" * 35, '\n'
        print studentName
        print "{path}/{student}/{cls}.java".format(path=path,student=studentName,cls=className)

        if not buildProc.poll():
            print "Wating for build to finish..."
            buildProc.wait()

        if buildProc.returncode != 0:
            print "{student}'s project didn't build".format(student=studentName)

        wrkpath = "{}/{}".format(path, studentName)

        os.chdir(wrkpath)

        ans = "y"
        while ans and ans.lower()[0] == 'y':
            if len(tests) == 1:
                key = tests.keys()[0]
            else:
                key = select_test()

            test = tests[key](studentName, className)

            print "Running test %s..." % key
            test.start()

            print "\nThe program got a score of {score}/{possible}".format(score=test.score(), possible=test.possible())
            if hasattr(test, 'output'):
                sel = raw_input("The test has output available. ([s]ave, [v]iew, [i]gnore)").lower()

                if sel == 'v':
                    print test.output()
                    sel = raw_input("Would you like to save it? (y/n)").lower()
                    sel = 's' if sel == 'y' else 'i'

                if sel == 's':
                    with open(key + "_output.log") as f:
                        f.write(test.output)
                    print "Output saved to " + key + "_output.log"

            print
            ans = raw_input("Program finished, do you want to rerun it? (y/n)")
            print

    os.chdir(path)
    t.join()


#end main

def select_test():
    keys = tests.keys()

    while True:
        print
        sel = raw_input("Which test would you like to run? (l to list)")

        if sel.lower() == 'l':
            print_numbered(keys)
            continue

        try:
            sel = int(sel)
        except ValueError:
            sel = 0

        if 0 < sel <= len(keys):
            return keys[sel-1]

        print "Invalid test number"

def print_numbered(l):
    for i in xrange(len(l)):
        print str(i+1) + ". " + str(l[i])

def do_builds(path, studentslist, que):

    for studentName, classes in studentslist:

        className = classes[0]  # For now we're assuming single file java projects

        wrkpath = "{}/{}".format(path, studentName)


        with open(wrkpath + "/build.log", "a") as log:  # Start logging for the build
            #Log entry header
            log.write('\n\n' + str(datetime.datetime.now()) + '\n')
            log.write("Starting build of %s.java\n\n" % className)

            #Make srcPath
            srcPath = [wrkpath] + className.split('.')  # Need to split on '.' to handle package cases
            srcPath = "/".join(srcPath) + '.java'

            #Do build, direct output to the log
            proc = subprocess.Popen(('javac', srcPath), stdout=log, stderr=log)

            que.put((studentName, className, proc)) # Add build to queue


def prepare_directory(path):
    """
    Prepares the grading directory by parsing the downloaded class files, separating them into student folders, and
    moving the java files to the corresponding directories.

    :param path: The directory to prepare
    :rtype : Dict the key is the students name, value is a list of class names
    """

    res = {}

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

        student = m.group(1)  #Get the student name from the match
        className = m.group(2)  #Get the className from the match
        destFile = "{}/{}/{}.java".format(path, student, className)
        origFile = "{}/{}".format(path, f)

        studentdir = "{}/{}".format(path, student)
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
                    destdir = "{}/{}/{}".format(path, student, package)

                    if not os.path.exists(destdir):
                        os.mkdir(destdir)

                    destFile = destdir + "/%s.java" % className

                    className = package + "." + className

        shutil.copy(origFile, destFile) #Copy the java file to the destination

        #Gets the class list for the student, if the student hasn't been added creates an empty list
        #Doing it this way allows for multifile java projects
        res.setdefault(student, []).append(className)


    return res


if __name__ == "__main__":
    main()
#end if
