__author__ = 'cory'

import os
import shutil
import uuid


class FileManager(object):
    """
    Static class to manage files that need to be copied and later removed.
    """

    history = {}

    @staticmethod
    def copy(paths, stuname):
        """
        Copies the files specified in .
        :param paths: a list of tuples consisting of (src, dst)
        :param stuName: name of student
        :return: a key to be to clean up files after tests are run
        """

        spaths = []
        for src, dst in paths:
            try:
                shutil.copy(src, dst)
                spaths.append((src, dst))
            except IOError, e:
                print str(e)

        record = {'name': stuname, 'paths': spaths}
        key = str(uuid.uuid4())
        FileManager.history[key] = record
        return key

    @staticmethod
    def clean(key):
        """
        Deletes the files associated with specified key
        :param key: a key that was returned when calling copy()
        """
        #stuname = FileManager.history[key]['name']
        paths = FileManager.history[key]['paths']

        for s, d in paths:
            if os.path.isfile(d):
                print "removing file %s." % d
                os.remove(d)
            else:
                shutil.rmtree(d) #directory