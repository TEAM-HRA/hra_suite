'''
Created on 15-08-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import os
    import gc
    import collections
    import pylab as pl
    from re import compile
    from pycore.misc import Params
    from pycore.units import Millisecond
    from pymath.utils.utils import USE_NUMPY_EQUIVALENT
    from pymath.utils.array_utils import array_copy
    from pymath.utils.array_utils import arrays_equal
except ImportError as error:
    print_import_error(__name__, error)

EMPTY_ARRAY = pl.array([])

ALL_ANNOTATIONS = -1

SignalNoBoundaryAnnotation = \
    collections.namedtuple('SignalNoBoundaryAnnotation',
                           ["signal", "annotation", "annotation_indexes"])


def exclude_boundary_annotations(_signal, _annotation, _excluded_annotations):
    """
    method removes boundary annotations from _annototion array and
    corresponding items from _signal array, returns named tuple
    SignalNoBoundaryAnnotation which includes new signal, new annotation
    array and indexes of remaining annotation values from _annontation
    array; what values are annotations is defined by _excluded_annotations
    parameter
    """
    if _annotation == None or \
        pl.sum(_annotation, dtype=int) == 0:
        return SignalNoBoundaryAnnotation(_signal, _annotation, None)

    #removing nonsinus beats from the beginning
    while (_annotation[0] != 0
            and (_excluded_annotations == ALL_ANNOTATIONS
                 or _annotation[0] in _excluded_annotations)):
        _signal = _signal[1:]
        _annotation = _annotation[1:]
        if len(_signal) == 0:
            break

    if len(_signal) > 0:
        #removing nonsinus beats from the end
        while (_annotation[-1] != 0
            and (_excluded_annotations == ALL_ANNOTATIONS
                or _annotation[-1] in _excluded_annotations)):
            _signal = _signal[:-1]
            _annotation = _annotation[:-1]
            if len(_signal) == 0:
                break

    annotation_indexes = get_annotation_indexes(_annotation,
                                                _excluded_annotations)
    return SignalNoBoundaryAnnotation(_signal, _annotation, annotation_indexes)


def get_annotation_indexes(_annotation, _excluded_annotations):
    """
    method returns indexes of annotation's values in _annotation parameter
    according to annotations defined by _excluded_annotations parameter
    """
    if len(_annotation) == 0:
        return EMPTY_ARRAY
    elif _excluded_annotations == ALL_ANNOTATIONS:
        return pl.array(pl.find(_annotation != 0))
    else:
        #find indexes of annotation array where values are in
        #_excluded_annotations list
        return pl.array(pl.where(
                    pl.in1d(_annotation, _excluded_annotations))[0], dtype=int)


def get_not_annotation_indexes(_annotation, _excluded_annotations):
    """
    method returns indexes of not annotation's values in _annotation parameter,
    annotation values are defined in _excluded_annotations parameter
    """
    if len(_annotation) == 0:
        return EMPTY_ARRAY
    elif _excluded_annotations == ALL_ANNOTATIONS:
        return pl.array(pl.find(_annotation == 0))
    else:
        #find indexes of an annotation array which are NOT included
        #in _excluded_annotations list
        return pl.array(pl.where(pl.logical_not(
                pl.in1d(_annotation, _excluded_annotations)))[0], dtype=int)


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

    def copy(self):
        """
        create copy of this DataVector object
        """
        return DataVector(
            signal=array_copy(self.signal),
            signal_plus=array_copy(self.signal_plus),
            signal_minus=array_copy(self.signal_minus),
            annotation=array_copy(self.annotation),
            signal_unit=self.signal_unit,
            time=array_copy(self.time))


EMPTY_DATA_VECTOR = DataVector(signal=EMPTY_ARRAY, signal_plus=EMPTY_ARRAY,
                               signal_minus=EMPTY_ARRAY, time=EMPTY_ARRAY,
                               annotation=EMPTY_ARRAY, signal_unit=None)


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


def get_unique_annotations(_annotations):
    if _annotations is not None:
        unique_annotations = pl.unique(_annotations)
        return unique_annotations[pl.where(unique_annotations > 0)]


class DataVectorAccessor(object):
    """
    class used to check if there are any changes in data_vector object
    and if this is the case all listeners are called
    """
    def __init__(self, _data_vector):
        # this is the first stage of data
        self.__data_vector0__ = _data_vector
        self.__data_vector__ = self.__data_vector0__.copy()
        self.__data_vector_listeners__ = {}
        # this member represents signal unit for x axis of a plot
        self.__x_signal_unit__ = None

    @property
    def data_vector(self):
        return self.__data_vector__

    @property
    def signal(self):
        return self.__data_vector__.signal

    @property
    def annotation(self):
        return self.__data_vector__.annotation

    @property
    def annotation0(self):
        """
        returns annotations of original state of data
        """
        return self.__data_vector0__.annotation

    @property
    def signal_unit(self):
        return self.__data_vector__.signal_unit

    @property
    def signal_x_unit(self):
        return self.__x_signal_unit__

    @property
    def signal_in_x_unit(self):
        """
        property expresses signal in signal x unit instead of original unit
        """
        if self.signal_unit == self.signal_x_unit:
            return self.signal
        multiplier = self.signal_unit.expressInUnit(self.signal_x_unit)
        return pl.cumsum(self.signal) * multiplier

    def addListener(self, _host, _data_vector_listener):
        self.__data_vector_listeners__[_host] = _data_vector_listener

    def changeSignal(self, _host, _signal, **params):
        if not arrays_equal(self.__data_vector__.signal, _signal):
            self.__data_vector__.signal = _signal
            for host in self.__data_vector_listeners__:
                if not _host == host:  # to avoid recurrence
                    self.__data_vector_listeners__[host].changeSignal(_signal,
                                                                     **params)

    def changeAnnotation(self, _host, _annotation, **params):
        if not arrays_equal(self.__data_vector__.annotation, _annotation):
            self.__data_vector__.annotation = _annotation
            for host in self.__data_vector_listeners__:
                if not _host == host:  # to avoid recurrence
                    self.__data_vector_listeners__[host].changeAnnotation(
                                                        _annotation, **params)

    def changeXSignalUnit(self, _host, _unit, **params):
        if not self.__x_signal_unit__ == _unit:
            self.__x_signal_unit__ = _unit
            for host in self.__data_vector_listeners__:
                if not _host == host:  # to avoid recurrence
                    self.__data_vector_listeners__[host].changeXSignalUnit(
                                                            _unit, **params)

    def restore(self, **params):
        """
        method used to be invoked to restore original state of data vector
        """
        if arrays_equal(self.__data_vector__.signal,
                        self.__data_vector0__.signal) and \
           arrays_equal(self.__data_vector__.annotation,
                         self.__data_vector0__.annotation):
            return
        self.__data_vector__ = None
        gc.collect()  # to force garbage collection
        self.__data_vector__ = self.__data_vector0__.copy()
        for host in self.__data_vector_listeners__:
            self.__data_vector_listeners__[host].changeSignal(
                                    self.__data_vector__.signal, **params)
            self.__data_vector_listeners__[host].changeAnnotation(
                                    self.__data_vector__.annotation, **params)


class DataVectorListener(object):
    """
    optional listener used when there are some changes in data vector
    to do specific actions
    """
    def changeSignal(self, _signal, **params):
        pass

    def changeAnnotation(self, _annotation, **params):
        pass

    def changeXSignalUnit(self, _signal_unit, **params):
        pass
