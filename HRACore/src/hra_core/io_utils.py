'''
Created on 20-10-2012

@author: jurek
'''

import sys
import collections
import os
from os import walk
from os import makedirs
import os.path as fs
from re import compile
from mimetypes import guess_type
from tailer import head  # @UnresolvedImport
from hra_core.misc import contains_letter
from hra_core.misc import get_separator_between_numbers
from hra_core.misc import Params
from hra_core.collections_utils import not_empty_nvl
from hra_core.collections_utils import get_ordered_list_of_strings
from hra_core.collections_utils import nvl


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
            if len(self.headers) > 0 and not separator == None \
                and len(separator.strip()) == 0:  # separator is a white space
                self.headers_count = len(self.headers[0].split())
            elif len(self.data) > 0 and not separator == None \
                and len(separator.strip()) == 0:  # separator is a white space
                self.headers_count = len(self.data[0].split())
            elif len(self.headers) > 0 and not separator == None:
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
        if separator == None:
            splited_lines = lines
        elif len(separator.strip()) == 0:  # separator is a white space
            splited_lines = [line.split() for line in lines]
        else:
            splited_lines = [line.split(separator) for line in lines]
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
    output_separator - a separator between output column data
    add_headers - if there will be output headers
    headers_order - includes ordered header names
    output_prefix - optional prefix added to output file name
    """
    def __init__(self, output_file=None, output_dir=None, output_suffix=None,
                 reference_filename=None, sort_headers=True,
                 ordinal_column_name=None, output_separator=None,
                 add_headers=False, ordered_headers=None,
                 output_prefix=None):
        self.__output_file__ = None
        self.__file__ = None  # means file descriptor
        self.__headers__ = None
        self.__sort_headers__ = sort_headers
        self.__ordinal_column_name__ = ordinal_column_name
        #force to take some output separator
        self.__output_separator__ = ',  ' \
                            if output_separator == None else output_separator
        #force to display headers
        self.__add_headers__ = add_headers
        self.__ordered_headers__ = ordered_headers
        if not output_file == None:
            self.__output_file__ = output_file
        elif not reference_filename == None:
            if output_dir == None:
                output_dir = fs.dirname(reference_filename)
            #prefix file with a label
            prefix_ = '' if output_prefix == None \
                    else output_prefix + "_"
            self.__output_file__ = normalize_filenames(output_dir,
                                    prefix_ + fs.basename(reference_filename) +
                                    not_empty_nvl(output_suffix, '_out'))
        if not self.__output_file__ == None:
            dir_ = fs.dirname(self.__output_file__)
            if fs.exists(dir_) == False:
                makedirs(dir_)

        self.__error_message__ = None
        self.__info_message__ = None

    def __enter__(self):
        self.__saved__ = False
        self.__error_message__ = None
        self.__info_message__ = None
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
                if not self.__ordered_headers__ == None:
                    self.__headers__ = get_ordered_list_of_strings(
                                            self.__ordered_headers__,
                                            self.__headers__)
                elif self.__sort_headers__:
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
            if self.__file__ == None and not self.__output_file__ == None:
                self.__file__ = open(self.__output_file__, "w")
            self.__file__.write(self.output_separator.join(values) + '\n')

    @property
    def headers(self):
        return self.__headers__

    @property
    def ordinal_column_name(self):
        return self.__ordinal_column_name__

    @property
    def output_separator(self):
        return self.__output_separator__

    @property
    def add_headers(self):
        return self.__add_headers__

    @property
    def error_message(self):
        return self.__error_message__

    @error_message.setter
    def error_message(self, _error_message):
        self.__error_message__ = _error_message

    @property
    def info_message(self):
        return self.__info_message__

    @info_message.setter
    def info_message(self, _info_message):
        self.__info_message__ = _info_message

    @property
    def saved(self):
        return self.__saved__

    @saved.setter
    def saved(self, _saved):
        self.__saved__ = _saved


def normalize_filenames(*iterator):
    """
    function normalized filenames
    """
    filenames = []
    fileparts = []
    for item in iterator:
        #special treatment item which have members filename and pathname
        if hasattr(item, 'filename') and hasattr(item, 'pathname'):
            filenames.append(fs.normpath(fs.join(item.pathname,
                                                 item.filename)))
        elif isinstance(item, list) or isinstance(item, tuple):
            normalized = normalize_filenames(*item)
            if isinstance(normalized, list) or isinstance(normalized, tuple):
                filenames[len(filenames):] = normalized
            else:
                filenames.append(normalized)
        else:
            #item could be a file already
            if fs.isfile(item):
                filenames.append(item)
            else:
                fileparts.append(item)
    if len(fileparts) > 0:
        filenames.append(fs.normpath(fs.join(*fileparts)))
    if len(filenames) == 1:
        return filenames[0]
    elif len(filenames) > 1:
        return filenames
    else:
        return None

PathAndFile = collections.namedtuple('PathAndFile', ["pathname", "filename"])


def path_and_file(_fullfilename):
    """
    tool function which splits full filename into named tuple PathAndFile
    """
    pathname = fs.dirname(_fullfilename)
    filename = fs.basename(_fullfilename)
    if pathname and filename:
        return PathAndFile(pathname, filename)


def as_path(*iterator):
    """
    function converts parts of path included in iterator into full path
    """
    return fs.normpath(fs.join(*iterator))


class FileSource(object):
    """
    class with some basic functionality
    """

    HEADER_PATTERN = compile(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]*')

    def __init__(self, **params):
        #params: _file, pathname, filename, separator
        self.params = Params(**params)
        self.__file__ = None
        if not self.params._file == None:
            self.__file__ = self.params._file
        elif not self.params.pathname == None and \
            not self.params.filename == None:
            self.__file__ = os.path.join(self.params.pathname,
                                         self.params.filename)
        self.__file_headers__ = None

        #number of lines of headers explicitly specified
        self.__headers_count__ = nvl(self.params.headers_count, 0)

        #contents of a file
        self.__file_data__ = None

    @property
    def headers(self):
        if self.__file_headers__ == None:
            self.__file_headers__ = []
            with open(self.__file__, 'r') as _file:
                for line in _file:
                    if not self.params.separator == None and \
                        len(self.params.separator.strip()) == 0:
                        headers = line.rstrip('\n').split()
                    else:
                        headers = line.rstrip('\n').split(self.params.separator)  # @IgnorePep8
                    header_ok = False
                    if self.__headers_count__ > 0:
                        header_ok = (len(self.__file_headers__)
                                                     < self.__headers_count__)
                    else:
                        for header in headers:
                            match = FileSource.HEADER_PATTERN.match(header) # @IgnorePep8
                            #to check if a header matches HEADER_PATTERN one
                            #have to test not only whether match is None but
                            #whether end() methods returns value > 0
                            if match is not None and match.end() > 0:
                                header_ok = True
                                break
                    if header_ok == False:
                        break
                    else:
                        self.__file_headers__.append(headers)
            self.__headers_count__ = len(self.__file_headers__)
            self.__headers_first_line__ = self.__file_headers__[0]

            #if there is only one row of headers then it is assumed that
            #headers are equivalent to this row
            if len(self.__file_headers__) == 1:
                self.__file_headers__ = self.__file_headers__[0]

        return self.__file_headers__

    @property
    def headers_with_col_index(self):
        return [list(enumerate(header)) for header in self.headers]

    @property
    def headers_first_line(self):
        self.headers  # to force headers's generation
        return self.__headers_first_line__

    @staticmethod
    def file_decorator(get_file_method):
        """
        a static decorator method use to avoid fetch the same data
        many times
        """
        def wrapped(_self=None):
            if _self.__file_data__ == None:
                _self.__file_data__ = get_file_method(_self)
            return _self.__file_data__
        return wrapped

    @property
    def source_filename(self):
        """
        returns source filename
        """
        return os.path.basename(self.__file__) if self.__file__ else None

    @property
    def source_pathname(self):
        """
        returns source pathname
        """
        return os.path.dirname(self.__file__) if self.__file__ else None

    @property
    def headers_count(self):
        self.headers  # to force headers's generation
        return self.__headers_count__

    @property
    def _file(self):
        return self.__file__


def create_dir(_dir):
    """
    create a dictionary if not present
    """
    if not fs.exists(_dir):
        os.mkdir(_dir)
