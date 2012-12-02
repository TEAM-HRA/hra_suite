'''
Created on 20-10-2012

@author: jurek
'''

from os.path import join
from os.path import exists
from os.path import pathsep
from os.path import dirname
from os import walk
from mimetypes import guess_type
from tailer import head  # @UnresolvedImport


def get_filenames(path, depth=1):
    filenames = []
    if (exists(path)):
        current_depth = 1
        for root, dirs, files in walk(path):  # @UnusedVariable
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
        for paths, dirnames, files in walk(path):  # @UnusedVariable
            full_filenames[len(full_filenames):] = [join(path, _file) #@IgnorePep8
                for _file in files if (extension == None or _file.endswith(extension))] #@IgnorePep8

    return pathsep.join(full_filenames) if as_string else full_filenames


def get_dirname(_file):
    return dirname(_file)


def is_text_file(filepath, only_known_types=False):
    filepath = str(filepath)
    filetype = guess_type(filepath)[0]
    if not filetype == None:
        if filetype.startswith('text'):
            return True
    else:
        if only_known_types == False:
            try:
                _file = file(filepath)
                headlines = head(_file, lines=3)
                _file.close()
                for line in headlines:
                    line.decode('ascii')
                return True
            except UnicodeError:
                pass
            except IOError:
                pass
    return False
