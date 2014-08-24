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


def main():
    if len(sys.argv) < 2:
        path = raw_input("Please enter the path (zip/folder): ")
    else:
        path = str(sys.argv[1])
    #end if

    path = os.path.abspath(path)  # Convert the path to an absolute path

    #TODO Test zip support
    # Fixed comparison to leverage negative indexes -Phillip Wall
    if '.zip' == path[-4:]:
        os.mkdir(path[:-4])

        with zipfile.ZipFile(path) as z:
            z.extractall(path=path[:-4])  # Extract the files

        path = path[:-4]  # Set path to newly created directory

    students = prepare_directory(path)

    for studentName, classes in students.iteritems():

        className = classes[0]  # For now we're assuming single file java projects

        wrkpath = "{}/{}".format(path, studentName)

        os.chdir(wrkpath)  # Change directory to the student's directory

        print "#" * 35, '\n'
        print studentName
        print "{path}/{student}/{cls}.java".format(path=path,student=studentName,cls=className)

        print "\nBuilding project..."

        with open("build.log", "a") as log:  # Start logging for the build
            #Log entry header
            log.write('\n\n' + str(datetime.datetime.now()) + '\n')
            log.write("Starting build of %s.java\n\n" % className)

            #Make srcPath
            srcPath = [wrkpath] + className.split('.')  # Need to split on '.' to handle package cases
            srcPath = "/".join(srcPath) + '.java'

            #Do build, direct output to the log
            code = subprocess.call(('javac', srcPath), stdout=log, stderr=log)

            #Check the return code to see if build was successful
            if code == 0:
                log.write("\n\nBuild successful\n")
            else:
                log.write("\n\nBuild was not sucessful\n")
                print "{student}'s project ({class}) did not build. See build log."

        print "Starting {student}'s project...".format(student=studentName)

        ans = ""
        while not ans.lower()[0] == 'y':
            #Run the program, gives it temporary control of the console
            subprocess.call(('java', className), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

            print '\n'
            ans = raw_input("Program finished, do you want to rerun it? (y/n)")
            print

    os.chdir(path)


#end main


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

        os.mkdir("{}/{}".format(path, student))

        classDeclaration = "public class " + className

        #Use context manager for handling file objects (no need to explicitly close the file) -Phillip Wall
        with open(origFile) as fHandle:
            for line in fHandle:
                if classDeclaration in line:
                    break
                if "package " in line:
                    #Strip trailing ';' with strip method -Phillip Wall
                    package = line.replace("package ", "").strip(';')
                    #1. create a new directory for the package
                    #2. Move the class file to the package directory

                    destFile = "{}/{}/{}/{}.java".format(path, student, package, className)

                    className = package + "." + className

        shutil.copy(origFile, destFile) #Copy the java file to the destination

        #Gets the class list for the student, if the student hasn't been added creates an empty list
        #Doing it this way allows for multifile java projects
        res.get(student, []).append(className)

    return res


if __name__ == "__main__":
    main()
#end if
