'''
Created on 29 maj 2013

@author: jurek
'''
try:
    import os
    import pylab as pl
    from re import compile
    from pycore.misc import Params
    from pymath.utils.utils import print_import_error
except ImportError as error:
    print_import_error(__name__, error)


class NumericalFileDataSource(object):
    """
    class to load numerical data file
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
        self.__headers_rows_count__ = 0
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
                    for header in headers:
                        match = NumericalFileDataSource.HEADER_PATTERN.match(header) # @IgnorePep8
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
            self.__headers_rows_count__ = len(self.__file_headers__)

            #if there is only one row of headers then it is assumed that
            #headers are equivalent to this row
            if len(self.__file_headers__) == 1:
                self.__file_headers__ = self.__file_headers__[0]

        return self.__file_headers__

    @property
    def headers_with_col_index(self):
        return [list(enumerate(header)) for header in self.headers]

    def getData(self):
        if self.__file_data__ == None:

            #to force headers's generation
            self.headers

            # check a separator is a white space
            if not self.params.separator == None and \
                len(self.params.separator.strip()) == 0:
                self.__file_data__ = pl.loadtxt(self.__file__,
                                         skiprows=self.__headers_rows_count__,
                                         unpack=True)
            else:
                self.__file_data__ = pl.loadtxt(self.__file__,
                                         skiprows=self.__headers_rows_count__,
                                         unpack=True,
                                         delimiter=self.params.separator)
        return self.__file_data__

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
