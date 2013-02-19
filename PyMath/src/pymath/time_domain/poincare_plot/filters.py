'''
Created on 27-07-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from numpy import array
    from pylab import find
    from pylab import arange
    from pylab import r_
    from pylab import in1d
    from pymath.utils.utils import USE_NUMPY_EQUIVALENT
    from pycore.introspection import create_class_object_with_suffix
    from pycore.introspection import get_method_arguments_count
    from pycore.introspection import get_subclasses_short_names
    from pymath.datasources import DataVector
    from pymath.statistics.statistics import StatisticsFactory
    from pymath.statistics.statistics import MeanStatistic
    from pymath.statistics.statistics import SDRRStatistic
    from pymath.statistics.statistics import NtotStatistic
    from pymath.statistics.statistics import TotTimeStatistic
except ImportError as error:
    print_import_error(__name__, error)


class FilterManager(object):
    def __init__(self):
        self.__filters__ = []

    def addFilter(self, _filter_object_or_handler_or_name, annotations=None):
        """
        filter entity could be passed as filter object itself, handler method
        or a name of filter class
        """
        if isinstance(_filter_object_or_handler_or_name, str):
            _filter_object_or_handler_or_name = \
                create_class_object_with_suffix(
                                'pymath.time_domain.poincare_plot.filters',
                                _filter_object_or_handler_or_name, 'Filter')
        _filter_object_or_handler_or_name.arg_count = \
            get_method_arguments_count(_filter_object_or_handler_or_name)
        self.__filters__.append(_filter_object_or_handler_or_name)

    def run(self, _data):
        """
        method which runs all filters as objects or as methods;
        when a method has two parameters it returns two values also
        when has a one parameter it returns one value
        when none parameters none value has to be returned
        """
        self.__statistics__ = {}
        data = _data
        for _filter in self.__filters__:
            if _filter.arg_count == -1:
                _filter.data = data
                data = _filter.filter()
                self.__statistics__.update(_filter.statistics)
            elif _filter.arg_count == 2:
                (data.signal, data.annotation) = _filter(data.signal,
                                                         data.annotation)
            elif _filter.arg_count == 1:
                data.signal = _filter(data.signal)
            elif _filter.arg_count == 0:
                _filter()
        return data

    def statistics(self):
        return getattr(self, '__statistics__', None)


class Filter(DataVector):
    '''
    classdocs
    '''

    def __init__(self, **data):
        '''
        Constructor
        '''
        DataVector.__init__(self, **data)
        self.statisticsClasses = None
        self.keepAnnotation = False

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    @property
    def filter(self):
        filteredData = None
        if not self.signal == None:
            filteredData = self.__filter__(self.signal, self.annotation)
            if not self.statisticsClasses == None:
                factory = StatisticsFactory(self.statisticsClasses)
                self.__statistics__ = factory.statistics(filteredData)
        if self.keepAnnotation:
            filteredData.annotation = self.annotation
        return filteredData

    def __filter__(self, _signal, _annotation=None):
        pass

    @property
    def statistics(self):
        return self.__statistics__

    @statistics.setter
    def statistics(self, statistics):
        self.__statistics__ = statistics

    @property
    def statisticsClasses(self):
        return self.__statistics_classes__

    @statisticsClasses.setter
    def statisticsClasses(self, statistics_classes):
        self.__statistics_classes__ = statistics_classes

    @property
    def keepAnnotation(self):
        return self.__keepAnnotation__

    @keepAnnotation.setter
    def keepAnnotation(self, _keepAnnotation):
        self.__keepAnnotation__ = _keepAnnotation

    @staticmethod
    def getSubclassesShortNames():
        return get_subclasses_short_names(Filter)


class RemoveAnnotationFilter(Filter):
    def __init__(self, data_source):
        Filter.__init__(self, data_source)
        self.statisticsClasses = (MeanStatistic, SDRRStatistic,
                              NtotStatistic, TotTimeStatistic)

    def __filter__(self, _signal, _annotation):
        if USE_NUMPY_EQUIVALENT:
            return DataVector(signal=_signal[_annotation == 0])

        indexy = array(find(_annotation == 0))
        return DataVector(signal=_signal[indexy],
                          annotation=_annotation[indexy])


class AnnotationShiftedPartsFilter(Filter):
    def __filter__(self, _signal, _annotation):
        #wykrywanie i usuwanie nonsinus na poczatku i na koncu
        while _annotation[0] != 0:
            _signal = _signal[1:-1]
            _annotation = _annotation[1:-1]
        #removing nonsinus beats from the end
        while _annotation[-1] != 0:
            _signal = _signal[0:-2]
            _annotation = _annotation[0:-2]
        indexy_p = array(find(_annotation != 0))
        indexy_m = indexy_p - 1
        indexy = r_[indexy_p, indexy_m]
        x_p = _signal[arange(0, len(_signal) - 1)]
        x_pp = _signal[arange(1, len(_signal))]
        x_p[indexy] = -1
        indexy = array(find(x_p != -1))
        x_p = x_p[indexy]
        x_pp = x_pp[indexy]
        return DataVector(signal=x_p, shifted_signal=x_pp)


class ZeroAnnotationFilter(Filter):
    def __init__(self, data_source, leave_annotations=(0,)):
        '''
        Constructor
        '''
        Filter.__init__(self, data_source)
        self.__leave_annotations__ = leave_annotations

    def __filter__(self, _signal, _annotation):
        if USE_NUMPY_EQUIVALENT:
            return self.__numpy_filter__(_signal, _annotation)

        for pobudzenie in self.__leave_annotations__:
            index_pobudzenie = find(_annotation == pobudzenie)
            index_pobudzenie = array(index_pobudzenie)
            if sum(index_pobudzenie != 0):
                _annotation[index_pobudzenie] = 0
        return DataVector(signal=_signal, annotation=_annotation)

    def __numpy_filter__(self, _signal, _annotation):
        if not self.__leave_annotations__ == (0,):
            _annotation[in1d(_annotation, self.__leave_annotations__)] = 0
        return DataVector(signal=_signal, annotation=_annotation)
