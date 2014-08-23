
##########################################################################
# Author:      Cory Nance												 
# Description: Script to grade labs   									 
# Date: 	   20 August 2014											 
# Assumptions: Submissions were mass-downloaded from Moodle and unzipped.
##########################################################################

import os
import sys

import subprocess
import zipfile
import re

def main():
    if len(sys.argv) < 2:
        path = raw_input("Please enter the path (zip/folder): ")
    else:
        path = str(sys.argv[1])
    #end if

    path = os.path.abspath(path) #Convert the path to a absolute path

    #TODO Test zip support
    # Fixed comparison to leverage negative indexes -Phillip Wall
    if '.zip' == path[-4:]:
        os.mkdir(path[:-4])

        with zipfile.ZipFile(path) as z:
            z.extractall(path=path[:-4]) #Extract the files

        path = path[:-4] #Set path to newly created directory


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

        ## Start author Phillip Wall
        m = regex.search(f) #Attempt to match the filename

        if not m:
            continue #If there is not a match this filename does not match the expected format, skip it.

        student = m.group(1) #Get the student name from the match
        className = m.group(2) #Get the className from the match
        tempFile = "{}/{}.java".format(path, className)
        realFile = "{}/{}".format(path, f)

        ## End author Phillip Wall

        classDeclaration = "public class " + className

        #Use context manager for handling file objects (no need to explicitly close the file) -Phillip Wall
        with open(realFile) as fHandle:
            for line in fHandle:
                if classDeclaration in line:
                    break
                if "package " in line:
                    #Strip trailing ';' with strip method -Phillip Wall
                    package = line.replace("package ", "").strip(';')
                    #1. create a new directory for the package
                    #2. Move the class file to the package directory

                    #Use the string format method to create the command to move the java file -Phillip Wall
                    cmd = 'mkdir "{path}/{package}"; mv "{path}/{name}.java" "{path}/{package}/{name}.java"'.format(
                        path=path, name=className, package=package)

                    # cmd = ( "mkdir \"" + path + "/" + package +
                    #         "\"; mv \"" + path + "/" + className +
                    #         ".class\" \"" + path + "/" + package + "/" +
                    #         className + ".class\""
                    # )

                    print cmd
                    os.system(cmd)
                    className = package + "." + className
            #end for line in f



        print "##################################\n"
        print student
        print realFile + "\n\n"


        
        cmds = []
        cmds.append( "cp \"" + realFile + "\" \"" + tempFile + "\"" )
        cmds.append( "javac \"" + tempFile + "\"" )
        cmds.append( "cd \"" + path + "\" && " + "java \"" + className + "\"" )

        for c in cmds:
            os.system(c)



        raw_input("Press enter to continue...")

        cmds = []
        cmds.append( "clear" )
        cmds.append( "rm -f " + tempFile )
        cmds.append( "vim \"" + realFile + "\"")

        for c in cmds:
            os.system(c)

        #end for f in files
#end main



if __name__ == "__main__":
    main()
#end if
