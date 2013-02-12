'''
Created on 10-02-2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import StringIO
    import numpy as np
    from pycore.io_utils import CSVFile
    from pycore.misc import fixed_size_string
    from pycore.collections_utils import get_as_tuple
except ImportError as error:
    print_import_error(__name__, error)


class NumpyCSVFile(CSVFile):
    def __init__(self,  output_file=None, output_dir=None, output_suffix=None,
                 reference_filename=None, sort_headers=True,
                 output_precision="10,5"):
        super(NumpyCSVFile, self).__init__(output_file, output_dir,
                    output_suffix, reference_filename, sort_headers)
        self.array_data = None
        self.__output_precision__ = get_as_tuple(output_precision, convert=int)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.output_file == None:
            memory_file = StringIO.StringIO()
            #write outcome to a file in memory
            np.savetxt(memory_file, self.array_data,
                fmt='%{0}.{1}f'.format(self.__output_precision__[0],
                                       self.__output_precision__[1]),
                delimiter=',  ')
            contents = memory_file.getvalue()
            _file = open(self.output_file, 'w')
            _file.write(self.__format_headers__(contents[:contents.find('\n')])) # @IgnorePep8
            _file.write(contents)
            _file.close()
            memory_file.close()

        self.array_data = None

    def write(self, _data):
        values = self.get_values(_data)
        if not values == None:
            if self.array_data == None:
                self.array_data = np.array(values)
                self.array_data = np.reshape(self.array_data, (1, len(values)))
            else:
                self.array_data = np.vstack([self.array_data, values])

    def __format_headers__(self, referenced_line):
        if not self.headers == None:
            sizes = map(len, referenced_line.split(','))
            return ','.join(map(fixed_size_string, self.headers, sizes)) + '\n'  # @IgnorePep8