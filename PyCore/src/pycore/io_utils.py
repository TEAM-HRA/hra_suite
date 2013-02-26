'''
Created on 20-10-2012

@author: jurek
'''

import sys
from os import walk
from os import makedirs
import os.path as fs
from mimetypes import guess_type
from tailer import head  # @UnresolvedImport
from pycore.misc import contains_letter
from pycore.misc import get_separator_between_numbers
from pycore.collections_utils import not_empty_nvl


def get_filenames(path, depth=1):
    filenames = []
    if (fs.exists(path)):
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

    if (fs.exists(path)):
        for paths, dirnames, files in walk(path):  # @UnusedVariable
            full_filenames[len(full_filenames):] = [fs.join(path, _file) #@IgnorePep8
                for _file in files if (extension == None or _file.endswith(extension))] #@IgnorePep8

    return fs.pathsep.join(full_filenames) if as_string else full_filenames


def get_dirname(_file):
    return fs.dirname(_file)


def is_text_file(filepath, only_known_types=False):
    filepath = str(filepath)
    filetype = guess_type(filepath)[0]
    if not filetype == None:
        if filetype.startswith('text'):
            return True
        if sys.platform == 'win32':
            return False

    if only_known_types == False:
        _file = None
        try:
            _file = file(filepath)
            headlines = head(_file, lines=3)
            for line in headlines:
                line.strip('\r\n').strip('\n').decode('ascii')
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
            _file = file(fs.join(*file_path)
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


class CSVFile(object):
    """
    class used to save data in csv format
    parameters:
    output_file - a file where data are saved
    output_dir - directory where file will be place
    reference_filename - a file used as a base to create output_file name
    output_suffix - a suffix appended to output_file
    sort_headers - whether to sort columns
    ordinal_column_name - name of the ordinal column,
                        this column will be the first one
    """
    def __init__(self, output_file=None, output_dir=None, output_suffix=None,
                 reference_filename=None, sort_headers=True,
                 ordinal_column_name=None):
        self.__output_file__ = None
        self.__file__ = None  # means file descriptor
        self.__headers__ = None
        self.__sort_headers__ = sort_headers
        self.__ordinal_column_name__ = ordinal_column_name

        if not output_file == None:
            self.__output_file__ = output_file
        elif not reference_filename == None:
            if output_dir == None:
                output_dir = fs.dirname(reference_filename)
            self.__output_file__ = fs.join(output_dir,
                                    fs.basename(reference_filename) +
                                      not_empty_nvl(output_suffix, '_out'))

        dir_ = fs.dirname(self.__output_file__)
        if fs.exists(dir_) == False:
            makedirs(dir_)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.__file__ == None:
            self.__file__.close()
            self.__file__ = None

    @property
    def output_file(self):
        return self.__output_file__

    def get_values(self, _data, _ordinal_value=None):
        values = None
        if isinstance(_data, dict):
            if self.__headers__ == None:
                self.__headers__ = _data.keys()
                if self.__sort_headers__:
                    self.__headers__ = sorted(self.__headers__)

                # move the ordinal column to the first position
                if self.ordinal_column_name:
                    if self.headers.count(self.ordinal_column_name) == 0:
                        self.headers.insert(0, self.ordinal_column_name)
                    else:
                        raise NameError('Ordinal column ' +
                                        self.ordinal_column_name +
                                        ' already exists in headers !')

            values = [_data.get(header, '') for header in self.headers]
            #replace value of the first ordinal position
            if self.ordinal_column_name and _ordinal_value is not None:
                values[0] = _ordinal_value
        return values

    def write(self, _data):
        values = self.get_values(_data)
        if not values == None:
            if self.__file__ == None and self.__output_file__:
                self.__file__ = open(self.__output_file__, "w")
            self.__file__.write(','.join(values) + '\n')

    @property
    def headers(self):
        return self.__headers__

    @property
    def ordinal_column_name(self):
        return self.__ordinal_column_name__
