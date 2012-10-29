'''
Created on 20-10-2012

@author: jurek
'''

import sys
from os.path import join
from os.path import exists
from os.path import pathsep
from os.path import dirname
from os import walk
from pycore.globals import GLOBALS


def get_program_path():
    return GLOBALS.PROGRAM_DIR if GLOBALS.PROGRAM_DIR else sys.path[0]


def get_filenames(path, depth=1):
    filenames = []
    if (exists(path)):
        current_depth = 1
        for root, dirs, files in walk(path):
            filenames[len(files):] = files
            if (current_depth == depth):
                break
            current_depth += 1
    else:
        return filenames


def expand_files(path, extension=None, as_string=False):
    full_filenames = []
    if extension:
        if extension.startswith("*."):
            extension = extension[1:]
        elif not extension.startswith("."):
            extension = "." + extension

    if (exists(path)):
        for paths, dirnames, files in walk(path):
            full_filenames[len(full_filenames):] = [join(path, file) #@IgnorePep8
                for file in files if (extension == None or file.endswith(extension))] #@IgnorePep8

    return pathsep.join(full_filenames) if as_string else full_filenames


def get_dirname(_file):
    return dirname(_file)
