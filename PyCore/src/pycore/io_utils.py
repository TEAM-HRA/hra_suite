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
            _file = None
            try:
                _file = file(filepath)
                headlines = head(_file, lines=3)
                for line in headlines:
                    line.decode('ascii')
                return True
            except UnicodeError:
                pass
            except IOError:
                pass
            finally:
                if not _file == None:
                    _file.close()
    return False


class DataFileHeader(object):

    def __init__(self, file_path, _separator=None, number_of_lines=5):
        headlines = []
        try:
            _file = file(join(*file_path)
                     if hasattr(file_path, '__iter__') else file_path)
            headlines = head(_file, number_of_lines)
            if len(headlines) > number_of_lines:
                headlines = headlines[:number_of_lines]
            _file.close()
        except UnicodeError:
            pass
        except IOError:
            pass

        #get lines with letters [a-z, A-Z]
        self.headers = [line for line in headlines \
                        if len(line) > 0 and contains_letter(line)]

        #get lines without letters [a-z, A-Z], national signs could be a problem @IgnorePep8
        self.data = [line for line in headlines \
                        if len(line) > 0 and not contains_letter(line)]

        self.initialize()
        self.separator = _separator

    def getSeparator(self, generate=False):
        if self.separator == None and generate:
            if len(self.data) > 0:
                self.separator = get_separator_between_numbers(self.data[0])
            elif len(self.headers) > 0:
                self.separator = get_separator_between_numbers(self.headers[0])
        return self.separator

    def initialize(self):
        self.headers_count = None
        self.headers_lines = None
        self.data_lines = None

    def setSeparator(self, separator):
        if not separator == self.getSeparator():
            self.initialize()
            self.separator = separator

    def getHeadersCount(self):
        if self.headers_count == None:
            separator = self.getSeparator()
            if len(self.headers) > 0 and not separator == None:
                self.headers_count = len(self.headers[0].split(separator))
            elif len(self.data) > 0 and not separator == None:
                self.headers_count = len(self.data[0].split(separator))
            elif len(self.headers) > 0 and separator == None:
                self.headers_count = 1
            elif len(self.data) > 0 and separator == None:
                self.headers_count = 1
            else:
                self.headers_count = 0
        return self.headers_count

    def getHeadersLines(self, number_of_lines=1):
        if self.headers_lines == None:
            self.headers_lines = self.__get_splited_lines__(self.headers)
        return self.headers_lines[:number_of_lines]

    def getDataLines(self):
        if self.data_lines == None:
            self.data_lines = self.__get_splited_lines__(self.data)
        return self.data_lines

    def __get_splited_lines__(self, lines):
        separator = self.getSeparator()
        splited_lines = lines if separator == None else \
                        [line.split(separator) for line in lines]
        if splited_lines == None:
            splited_lines = [str(num)
                             for num in range(1, self.getHeadersCount())]
        return splited_lines
