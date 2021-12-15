#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Global module variables and subroutines for pyramses."""

import errno
import inspect
import os

__runTimeObs__ = True
__libdir__ = os.path.realpath(
    os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "libs")))


def CustomWarning(message, category, filename, lineno, file=None, line=None):
    """Custom routine to print warnings."""
    print("RAMSESWarning: %s" % message)


def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class RAMSESError(Exception):
    pass


def __which(program):
    """Check the path for a program and if it's executable."""

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def silentremove(filename):
    """Check if a file exists and delete it
    
    :type filename: str
    """

    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occured

def wrapToList(item):
    """Wraps item into a list if it's not already a list.
    """
    if not isinstance(item, list):
        return [item]
    else:
        return item

    