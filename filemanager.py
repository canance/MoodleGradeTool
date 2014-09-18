__author__ = 'cory'

import os
import shutil
import uuid

history = {}


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