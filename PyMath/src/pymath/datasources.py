'''
Created on 15-08-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import os
    import numpy as np
    from re import compile
    from pycore.misc import Params
    from pycore.units import Millisecond
    from pymath.utils.utils import USE_NUMPY_EQUIVALENT
except ImportError as error:
    print_import_error(__name__, error)


class DataVector(object):

    def __init__(self, **params):
        '''
        Constructor
        '''
        self.__params__ = Params(**params)
        if self.__params__.signal_unit is None:
            self.__params__.signal_unit = Millisecond

    @property
    def signal(self):
        return self.__params__.signal

    @signal.setter
    def signal(self, _signal):
        self.__params__.signal = _signal

    @property
    def annotation(self):
        return self.__params__.annotation

    @annotation.setter
    def annotation(self, _annotation):
        self.__params__.annotation = _annotation

    @property
    def time(self):
        return self.__params__.time

    @time.setter
    def time(self, _time):
        self.__params__.time = _time

    @property
    def signal_plus(self):
        return self.__params__.signal_plus

    @signal_plus.setter
    def signal_plus(self, _signal_plus):
        self.__params__.signal_plus = _signal_plus

    @property
    def signal_minus(self):
        return self.__params__.signal_minus

    @signal_minus.setter
    def signal_minus(self, _signal_minus):
        self.__params__.signal_minus = _signal_minus

    @property
    def signal_unit(self):
        return self.__params__.signal_unit

    @signal_unit.setter
    def signal_unit(self, _signal_unit):
        self.__params__.signal_unit = _signal_unit

    @property
    def data(self):
        pass

    @data.setter
    def data(self, _data):
        self.__params__ = Params(signal=_data.signal,
                                 signal_plus=_data.signal_plus,
                                 signal_minus=_data.signal_minus,
                                 annotation=_data.annotation,
                                 signal_unit=_data.signal_unit,
                                 time=_data.time)
        #raise Exception('Parameter data have to be of DataSource type !!!')

    def __str__(self):
        return (' '.join(
            [self.__for_str__('signal', self.__params__.signal),
             self.__for_str__('signal_plus', self.__params__.signal_plus),
             self.__for_str__('signal_minus', self.__params__.signal_minus),
             self.__for_str__('annotation', self.__params__.annotation),
             self.__for_str__('time', self.__params__.time)]))

    def __for_str__(self, prefix, data):
        if hasattr(data, 'take') or hasattr(data, '__getslice__'):
            l = len(data)
            if hasattr(data, 'take'):
                sample = data.take(range(10 if l > 10 else l))
            elif hasattr(data, '__getslice__'):
                sample = data[0:(10 if l > 10 else l)]
            return ("{0} [size {1} sample {2}] ".format(prefix, l, sample))
        return ''

    # if parameter is not set in the __init__() method then returns None
    def __getattr__(self, name):
        return None


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
                contents = line.split(self.params.separator)
                for index in self.__cols__:
                    _data[index].append(contents[self.__cols__[index]])

        return self.__createData__(map(np.array, _data))

    def __getNumPyData__(self):
        _data = [None] * len(self.__cols__)
        _data = np.loadtxt(self.__file__,
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
        data = self.getData()
        if data.annotation is not None:
            unique_annotations = np.unique(data.annotation)
            return unique_annotations[np.where(unique_annotations > 0)]
