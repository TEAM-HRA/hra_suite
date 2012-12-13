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
from pycore.misc import contains_letter
from pycore.misc import get_separator_between_numbers


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


def get_headers_for_datafile(file_path, _separator=None, lines_number=5):
    try:
        #file_path could be an iterable with separated path's parts
        #or the whole file path
        _file = file(join(*file_path)
                     if hasattr(file_path, '__iter__') else file_path)
        headlines = head(_file, lines_number)
        _file.close()

        #get lines with letters [a-z, A-Z]
        header_lines = [line for line in headlines if contains_letter(line)]

        #get lines without letters [a-z, A-Z], national signs could be a problem @IgnorePep8
        data_lines = [] if _separator else \
                    [line for line in headlines if not contains_letter(line)]

        if len(data_lines) > 0 or _separator:
            #if _separator not exists get a separator from
            #the first non-letters line
            separator = _separator if _separator \
                            else get_separator_between_numbers(data_lines[0])
            if separator:
                #split all headers lines according to the passed/founded separator @IgnorePep8
                headers = [header.split(separator) for header in header_lines]
                return headers
    except UnicodeError:
        pass
    except IOError:
        pass
