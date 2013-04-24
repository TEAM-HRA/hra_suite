'''
Created on 24 kwi 2013

@author: jurek
'''
try:
    import os
    import pylab as pl
    from re import compile
    from pycore.misc import Params
    from pymath.utils.utils import USE_NUMPY_EQUIVALENT
    from pymath.utils.utils import print_import_error
    from pymath.model.data_vector import DataVector
    from pymath.model.utils import get_unique_annotations
except ImportError as error:
    print_import_error(__name__, error)


class FileDataSource(object):

    HEADER_PATTERN = compile(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]*')
    SIGNAL_IDENT = 'S'
    ANNOTATION_IDENT = 'A'
    TIME_IDENT = 'T'

    def __init__(self, **params):
        #params: pathname, filename, signal_index, annotation_index, time_index, separator @IgnorePep8
        self.params = Params(**params)
        self.__file__ = None
        if not self.params._file == None:
            self.__file__ = self.params._file
        elif not self.params.pathname == None and \
            not self.params.filename == None:
            self.__file__ = os.path.join(self.params.pathname,
                                         self.params.filename)
        self.__headers__ = None
        self.__cols__ = []
        self.__cols_idents__ = ""
        if self.params.signal_index >= 0:
            self.__cols__.append(self.params.signal_index)
            self.__cols_idents__ += FileDataSource.SIGNAL_IDENT
        if self.params.annotation_index >= 0:
            self.__cols__.append(self.params.annotation_index)
            self.__cols_idents__ += FileDataSource.ANNOTATION_IDENT
        if self.params.time_index >= 0:
            self.__cols__.append(self.params.time_index)
            self.__cols_idents__ += FileDataSource.TIME_IDENT

    @property
    def headers(self):
        if self.__headers__ == None:
            self.__headers__ = []
            with open(self.__file__, 'r') as _file:
                for line in _file:
                    if not self.params.separator == None and \
                        len(self.params.separator.strip()) == 0:
                        headers = line.rstrip('\n').split()
                    else:
                        headers = line.rstrip('\n').split(self.params.separator)  # @IgnorePep8
                    header_ok = False
                    for header in headers:
                        match = FileDataSource.HEADER_PATTERN.match(header)
                        #to check if a header matches HEADER_PATTERN one
                        #have to test not only whether match is None but
                        #whether end() methods returns value > 0
                        if match is not None and match.end() > 0:
                            header_ok = True
                            break
                    if header_ok == False:
                        break
                    else:
                        self.__headers__.append(headers)
        return self.__headers__

    @property
    def headers_with_col_index(self):
        return [list(enumerate(header)) for header in self.headers]

    def getData(self):
        return self.__getNumPyData__() if USE_NUMPY_EQUIVALENT else \
               self.__getSimpleData__()

    def __getSimpleData__(self):

        _data = [[]] * len(self.__cols__)
        with open(self.__file__, 'r') as _file:
            for _ in range(len(self.headers)):  # skip header lines
                _file.readline()

            for line in _file:
                #contents = findall(r'\b[0-9\.]+', line)
                if not self.params.separator == None and \
                    len(self.params.separator.strip()) == 0:
                    contents = line.split()
                else:
                    contents = line.split(self.params.separator)
                for index in self.__cols__:
                    _data[index].append(contents[self.__cols__[index]])

        return self.__createData__(map(pl.array, _data))

    def __getNumPyData__(self):
        _data = [None] * len(self.__cols__)
        # check a separator is a white space
        if not self.params.separator == None and \
            len(self.params.separator.strip()) == 0:
            _data = pl.loadtxt(self.__file__,
                               skiprows=len(self.headers),
                               usecols=self.__cols__,
                               unpack=True)
        else:
            _data = pl.loadtxt(self.__file__,
                               skiprows=len(self.headers),
                               usecols=self.__cols__,
                               unpack=True,
                               delimiter=self.params.separator)
        #if only one column is pick up then _data variable contains only
        #one numpy array so it have to be enclosed as list type
        return self.__createData__([_data] if len(self.__cols__) == 1 \
                                   else _data)

    def __createData__(self, _data):
        indexes = map(self.__cols_idents__.find,
                      [FileDataSource.SIGNAL_IDENT,
                       FileDataSource.ANNOTATION_IDENT,
                       FileDataSource.TIME_IDENT])
        (signal, annotation, time) = \
              [(None if index == -1 else \
                _data[index:index + 1][0]) for index in indexes]
        if annotation == None and not signal == None:
            annotation = 0 * signal
        if not annotation == None:
            annotation = annotation.astype(int)

        data_source = DataVector(signal=signal, annotation=annotation,
                                 time=time)
        data_source.filename = self.__file__  # set up an additional property
        return data_source

    def getUniqueAnnotations(self):
        return get_unique_annotations(self.getData().annotation)
