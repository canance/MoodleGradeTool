"""Module for all file management functions. Handles preparing the grading directory, copying files the tests need, and
cleaning up after the tests are done. """

__author__ = 'cory'

import re
import zipfile

import os
import shutil
import uuid
from collections import namedtuple
from . import student

history = {}

FileMapping = namedtuple('FileMapping', ('source', 'destination'))

Student = student.Student

def copy(src, dst):
    """
    Copies the files to the students working path.

    :param paths: a list of tuples consisting of (src_file, dst_file)
    :param stuName: name of student
    :return: a key to be used when the resources need to be cleaned (removed)
    """
    spaths = []
    try:
        shutil.copy(src, dst)
        spaths.append((src, dst))
    except IOError, e:
        print str(e)


    record = {'name': None, 'paths': spaths}
    key = str(uuid.uuid4())
    history[key] = record
    return key

def bulkcopy(paths, stuname):
    """
    Copies the files to the students working path.

    :param paths: a list of tuples consisting of (src_file, dst_file)
    :param stuName: name of student
    :return: a key to be used when the resources need to be cleaned (removed)
    """
    spaths = []
    for s, d in paths:
        try:
            dst = "%s/%s" % (stuname, d)
            shutil.copy(s, dst)
            spaths.append((s, d))
        except IOError, e:
            print str(e)

    record = {'name': stuname, 'paths': spaths}
    key = str(uuid.uuid4())
    history[key] = record
    return key


def clean(key):
    """
    Deletes the files associated with specified key

    :param key: a key that was returned when calling copy()
    """
    record = history.pop(key)
    stuname = record['name']
    paths = record['paths']
    if stuname is not None:
        for s, d in paths:
            dst = "%s/%s" % (stuname, d)
            if os.path.isfile(dst):
                os.remove(dst)
            else:
                shutil.rmtree(dst)
    else:
        for src, dst in paths:
            if os.path.isfile(dst):
                os.remove(dst)
            else:
                shutil.rmtree(dst)


def prepare_single_file(studentname, filename, path, f, tmp):
    classname = filename
    destfile = "{}/{}/{}.java".format(path, studentname, classname)
    origfile = "{}/{}".format(path, f)
    spath = "{}/{}".format(path, studentname)
    studentdir = "{}/{}".format(path, studentname)
    if not os.path.exists(studentdir):
        os.mkdir(studentdir)

    destfile, classname, package = find_package(origfile, destfile, classname, spath)
    shutil.copy(origfile, destfile) #Copy the java file to the destination

    #Gets the class list for the student, if the student hasn't been added creates an empty list
    #Doing it this way allows for multifile java projects
    tmp.setdefault(studentname, []).append(classname)


def prepare_directory(path):
    """
    Prepares the grading directory by parsing the downloaded class files, separating them into student folders, and
    moving the java files to the corresponding directories.
    Returns a dict with the students name as the key, and list of java classes as the value.

    :param path: The directory to prepare
    :rtype: Dict
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
        filename = m.group(2)  #Get the file name from the match

        if f[-5:] == '.java': #single file
            prepare_single_file(studentname, filename, path, f, tmp)
        elif f[-4:] == '.zip': #zip file
            prepare_zip_file(studentname, filename, path, f, tmp)

    res = []
    for name, cl in tmp.iteritems():
        main = cl.pop(0)  # Assume first class is the main one
        res.append(Student(name, main, cl))

    return res


def prepare_zip_file(studentname, filename, path, f, tmp):
    studentdir = "{}/{}".format(path, studentname)
    if not os.path.exists(studentdir):
        os.mkdir(studentdir)

    if f[-4:] == '.zip':
        zip = "{}/{}".format(path, f)
        zipdir = "{}/{}".format(path, f[:-4])
        if not os.path.exists(zipdir):
            os.mkdir(zipdir)

        with zipfile.ZipFile(zip) as z:
                z.extractall(path=zipdir)
    else:
        zipdir = f

    files = os.listdir(zipdir)

    for f in files:
        if f[-5:] == '.java':
            origfile = "{}/{}".format(zipdir, f)
            destfile = "{}/{}".format(studentdir, f)
            spath = "{}/{}".format(path, studentname)
            classname = f[:-5]
            destfile, classname, package = find_package(origfile, destfile, classname, spath)
            shutil.copy(origfile, destfile)
            tmp.setdefault(studentname, []).append(classname)
        elif os.path.isdir(zipdir + "/" + f):
            prepare_zip_file(studentname, filename, path, zipdir + "/" + f, tmp)
    shutil.rmtree(zipdir)


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