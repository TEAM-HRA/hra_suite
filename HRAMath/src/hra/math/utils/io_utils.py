'''
Created on 10-02-2013

@author: jurek
'''
from hra.math.utils.utils import print_import_error
try:
    import gc
    import StringIO
    import numpy as np
    from hra.core.io_utils import CSVFile
    from hra.core.misc import fixed_size_string
    from hra.core.collections_utils import get_as_tuple
    from hra.core.collections_utils import nvl
except ImportError as error:
    print_import_error(__name__, error)


class NumpyCSVFile(CSVFile):
    def __init__(self,  output_file=None, output_dir=None, output_suffix=None,
                 reference_filename=None, sort_headers=True,
                 output_precision=None, print_output_file=False,
                 ordinal_column_name=None, output_separator=None,
                 add_headers=False, ordered_headers=None,
                 message=None):
        super(NumpyCSVFile, self).__init__(output_file, output_dir,
                    output_suffix, reference_filename, sort_headers,
                    ordinal_column_name=ordinal_column_name,
                    output_separator=output_separator,
                    add_headers=add_headers,
                    ordered_headers=ordered_headers)
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
                    _file.write(self.__format_headers__(contents[:contents.find('\n')])) # @IgnorePep8
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

    def __format_headers__(self, referenced_line):
        if not self.headers == None:
            if len(self.output_separator.strip()) == 0:
                sizes = map(len, referenced_line.split())
            else:
                sizes = map(len, referenced_line.split(self.output_separator))
            return self.output_separator.join(map(fixed_size_string, self.headers, sizes)) + '\n'  # @IgnorePep8
