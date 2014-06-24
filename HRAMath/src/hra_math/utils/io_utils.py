'''
Created on 10-02-2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import os
    import gc
    import StringIO
    import numpy as np
    from hra_core.io_utils import get_filename
    from hra_core.io_utils import CSVFile
    from hra_core.misc import fixed_size_string
    from hra_core.collections_utils import get_as_tuple
    from hra_core.collections_utils import nvl
except ImportError as error:
    print_import_error(__name__, error)


class NumpyCSVFile(CSVFile):
    def __init__(self,  output_file=None, output_dir=None, output_suffix=None,
                 reference_filename=None, sort_headers=True,
                 output_precision=None, print_output_file=False,
                 ordinal_column_name=None, output_separator=None,
                 add_headers=False, ordered_headers=None,
                 message=None, output_prefix=None,
                 ordered_headers_aliases=None):
        super(NumpyCSVFile, self).__init__(output_file, output_dir,
                    output_suffix, reference_filename, sort_headers,
                    ordinal_column_name=ordinal_column_name,
                    output_separator=output_separator,
                    add_headers=add_headers,
                    ordered_headers=ordered_headers,
                    output_prefix=output_prefix,
                    ordered_headers_aliases=ordered_headers_aliases)
        self.array_data = None
        self.__output_precision__ = get_as_tuple(output_precision, convert=int)
        self.__print_output_file__ = print_output_file
        self.__message__ = message

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.output_file == None:
            if not self.array_data == None:
                #write outcome to a file in memory
                memory_file = StringIO.StringIO()
                if self.__output_precision__ == None:
                    np.savetxt(memory_file, self.array_data,
                               delimiter=self.output_separator)
                else:
                    np.savetxt(memory_file, self.array_data,
                           fmt='%{0}.{1}f'.format(self.__output_precision__[0],
                                                self.__output_precision__[1]),
                           delimiter=self.output_separator)
                contents = memory_file.getvalue()
                _file = open(self.output_file, 'w')
                if self.add_headers:
                    _file.write(self.__format_headers__(
                                    contents[:contents.find('\n')],
                                    nvl(self.headers_aliases, self.headers)))
                _file.write(contents)
                _file.close()
                self.saved = True
                memory_file.close()
                memory_file = None
                if self.__print_output_file__:
                    self.info_message = nvl(self.__message__,
                                        'Data saved into the file: ') + \
                                        self.output_file
            else:
                self.info_message = 'No data saved !!!'
        self.array_data = None
        gc.collect()

    def write(self, _data, ordinal_value=None):
        values = self.get_values(_data, ordinal_value)
        if not values == None:
            if self.array_data == None:
                self.array_data = np.array(values)
                self.array_data = np.reshape(self.array_data, (1, len(values)))
            else:
                self.array_data = np.vstack([self.array_data, values])

    def __format_headers__(self, referenced_line, _headers):
        if not _headers == None:
            if len(self.output_separator.strip()) == 0:
                sizes = map(len, referenced_line.split())
            else:
                sizes = map(len, referenced_line.split(self.output_separator))
            return self.output_separator.join(map(fixed_size_string, _headers, sizes)) + '\n'  # @IgnorePep8


def save_arrays_into_file(filename, *arrays):
    """
    function saves collections of arrays as numpy arrays into a file;
    arrays need not to be an equal size, shorter arrays are align
    to maximum sized array by adding 0;
    all data are saved as 15 character long strings
    """
    # get max size of collections
    max_size = np.amax(np.array([map(len, arrays)]))

    # align all arrays to maximum size by adding 0 values
    arrays = [np.append(a_, np.zeros(max_size - len(a_))) for a_ in arrays]

    arrays = np.column_stack(tuple(arrays))
    np.savetxt(filename, arrays, fmt='%15s')


def shuffle_file(_file, headers_count=0, output_dir=None, shuffled_prefix='S_'):
    """
    shuffle contexts of a text file
    """
    if not output_dir:
        output_dir = os.path.abspath(_file)
    shuffled_filename = shuffled_prefix + get_filename(_file, with_extension=True)
    shuffled_file = os.path.join(output_dir, shuffled_filename)
    with open(_file, 'r') as _f:
        file_data = [line for line in _f]
        shuffled_idxs = np.random.permutation(len(file_data) - 1) \
                    + headers_count
        with open(shuffled_file, 'w') as _shuffled_file:
            #write header lines
            for line in file_data[:headers_count]:
                _shuffled_file.write(line)
            for i in np.arange(headers_count, len(file_data)):
                _shuffled_file.write(file_data[shuffled_idxs[i - 1]])
    return shuffled_file
