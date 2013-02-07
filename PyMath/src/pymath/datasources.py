'''
Created on 15-08-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import glob
    import os
    from re import findall
    from re import compile
    from numpy import array
    from numpy import loadtxt
    from pymath.utils.utils import USE_NUMPY_EQUIVALENT
    from pymath.utils.utils import Params
except ImportError as error:
    print_import_error(__name__, error)


class DataSource(object):

    def __init__(self, signal=None, annotation=None, time=None):
        '''
        Constructor
        '''
        if (isinstance(signal, DataSource)):
            self.signal = signal.signal
            self.annotation = signal.annotation
            self.time = signal.time
        else:
            self.signal = signal
            self.annotation = annotation
            self.time = time

    @property
    def signal(self):
        return self.__signal__

    @signal.setter
    def signal(self, signal):
        self.__signal__ = signal

    @property
    def annotation(self):
        return self.__annotation__

    @annotation.setter
    def annotation(self, annotation):
        self.__annotation__ = annotation

    @property
    def time(self):
        return self.__time__

    @time.setter
    def time(self, time):
        self.__time__ = time

    def __str__(self):
        return (self.__for_str__('signal', self.signal) + ' '
              + self.__for_str__('annotation', self.annotation)
              + self.__for_str__('time', self.time))

    def __for_str__(self, prefix, data):
        if hasattr(data, 'take') or hasattr(data, '__getslice__'):
            l = len(data)
            if hasattr(data, 'take'):
                sample = data.take(range(10 if l > 10 else l))
            elif hasattr(data, '__getslice__'):
                sample = data[0:(10 if l > 10 else l)]
            return ("{0} [size {1} sample {2}] ".format(prefix, l, sample))
        return ''


class ColumnSpec(object):
    def __init__(self, header):
        self.header = header
        self.num = -1

    @property
    def num(self):
        return self.__num__

    @num.setter
    def num(self, num):
        self.__num__ = num

    @property
    def header(self):
        return self.__header__

    @header.setter
    def header(self, header):
        self.__header__ = header


class AnnotationColumnSpec(ColumnSpec):
    pass


class SignalColumnSpec(ColumnSpec):
    pass


class TimeColumnSpec(ColumnSpec):
    pass


class FilesDataSources(object):

    def __init__(self, path, ext=None):

        self.__idx__ = 0
        self.__headers__ = []
        self.__filenames__ = []
        self.__signal_spec__ = None
        self.__annotation_spec__ = None
        self.__cols__ = []

        path = path + ('*.*' if ext == None else ext)
        for filename in glob.glob(path):
            if os.path.isfile(filename):
                self.__filenames__.append(filename)

    def setColumnsSpecs(self, signal_spec, annotation_spec):
        self.__signal_spec__ = self.__fillNum__(signal_spec)
        self.__annotation_spec__ = self.__fillNum__(annotation_spec)

    def __fillNum__(self, spec):
        if spec:
            spec.num = None
            for num, header in enumerate(self.headers, start=0):
                if spec.header == header:
                    spec.num = num
                    self.__cols__.append(num)
                    break
        return spec

    def __iter__(self):
        return self

    def next(self):
        if self.__filenames__ and len(self.__filenames__) > self.__idx__:
            self.__idx__ += 1
            filename = self.__filenames__[self.__idx__ - 1]
            if USE_NUMPY_EQUIVALENT:
                return self.__getNumPyDataSource__(filename)
            else:
                return self.__getDataSource__(filename)
        else:
            raise StopIteration

    @property
    def headers(self):
        if not self.__headers__:
            with open(self.__filenames__[0], 'r') as _file:
                header_line = _file.readline()  # header line
                self.__headers__ = findall(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]+', header_line) #@IgnorePep8
        return self.__headers__

    def __getDataSource__(self, filename):
        signal = []
        annotation = []

        with open(filename, 'r') as _file:
            _file.readline()  # skip header line
            for line in _file:
                contents = findall(r'\b[0-9\.]+', line)
                if self.signal_spec:
                    signal.append(float(contents[self.signal_spec.num]))
                if self.annotation_spec:
                    annotation.append(int(float(contents[self.annotation_spec.num]))) #@IgnorePep8

        return self.__createDataSource__(filename, array(signal), array(annotation)) #@IgnorePep8

    @property
    def signal_spec(self):
        return self.__signal_spec__

    @property
    def annotation_spec(self):
        return self.__annotation_spec__

    @property
    def cols(self):
        return self.__cols__

    def __getNumPyDataSource__(self, filename):
        signal = None
        annotation = None

        if len(self.cols) == 2:
            (signal, annotation) = loadtxt(filename,
                                           skiprows=1,
                                           usecols=self.cols,
                                           unpack=True)
            annotation = annotation.astype(int)
        else:
            signal = loadtxt(filename,
                             skiprows=1,
                             usecols=self.cols,
                             unpack=True)

        return self.__createDataSource__(filename, signal, annotation)

    def __createDataSource__(self, filename, signal, annotation):
        if (self.annotation_spec and self.signal_spec
            and self.signal_spec.num == self.annotation_spec.num):
            annotation = 0 * signal

        data_source = DataSource(signal, annotation)
        data_source.filename = filename  # set up an additional property
        return data_source


class FileDataSource(object):

    HEADER_PATTERN = compile(r'\b[A-Za-z\[\]\-\%\#\!\@\$\^\&\*]*')
    SIGNAL_IDENT = 'S'
    ANNOTATION_IDENT = 'A'
    TIME_IDENT = 'T'

    def __init__(self, **params):
        #params: pathname, filename, signal_index, annotation_index, time_index, separator @IgnorePep8
        self.params = Params(**params)
        self.__file__ = os.path.join(self.params.pathname, self.params.filename) # @IgnorePep8
        self.__headers__ = None
        self.__cols__ = []
        self.__cols_idents__ = ""
        if self.params.signal_index:
            self.__cols__.append(self.params.signal_index)
            self.__cols_idents__ += FileDataSource.SIGNAL_IDENT
        if self.params.annotation_index:
            self.__cols__.append(self.params.annotation_index)
            self.__cols_idents__ += FileDataSource.ANNOTATION_IDENT
        if self.params.time_index:
            self.__cols__.append(self.params.time_index)
            self.__cols_idents__ += FileDataSource.TIME_IDENT

    @property
    def headers(self):
        if self.__headers__ == None:
            self.__headers__ = []
            with open(self.__file__, 'r') as _file:
                header_ok = False
                for line in _file:
                    headers = line.rstrip('\n').split(self.params.separator)
                    for header in headers:
                        if FileDataSource.HEADER_PATTERN.match(header):
                            header_ok = True
                            break
                    if header_ok == False:
                        break
                self.__headers__.append(headers)
        return self.__headers__

    def getDataSource(self):
        return self.__getNumPyDataSource__() if USE_NUMPY_EQUIVALENT else \
               self.__getSimpleDataSource__()

    def __getSimpleDataSource__(self):

        _data = [[]] * len(self.__cols__)
        with open(self.__file__, 'r') as _file:
            for _ in range(len(self.headers)):  # skip header lines
                _file.readline()

            for line in _file:
                #contents = findall(r'\b[0-9\.]+', line)
                contents = line.split(self.params.separator)
                for index in self.__cols__:
                    _data[index].append(contents[self.__cols__[index]])

        return self.__createDataSource__(map(array, _data))

    def __getNumPyDataSource__(self):
        _data = [None] * len(self.__cols__)
        _data = loadtxt(self.__file__,
                        skiprows=len(self.headers),
                        usecols=self.__cols__,
                        unpack=True,
                        delimiter=self.params.separator)
        return self.__createDataSource__(_data)

    def __createDataSource__(self, _data):
        indexes = map(self.__cols_idents__.find,
                      [FileDataSource.SIGNAL_IDENT,
                       FileDataSource.ANNOTATION_IDENT,
                       FileDataSource.TIME_IDENT])
        (signal, annotation, time) = \
              [(None if index == -1 else \
                _data[index:index + 1][0]) for index in indexes]
        if annotation == None:
            annotation = 0 * signal
        if not annotation == None:
            annotation = annotation.astype(int)

        data_source = DataSource(signal, annotation, time)
        data_source.filename = self.__file__  # set up an additional property
        return data_source
