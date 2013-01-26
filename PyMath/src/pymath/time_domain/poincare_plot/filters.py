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
    from pymath.datasources import DataSource
    from pymath.statistics.statistics import StatisticsFactory
    from pymath.statistics.statistics import MeanStatistic
    from pymath.statistics.statistics import SDRRStatistic
    from pymath.statistics.statistics import NtotStatistic
    from pymath.statistics.statistics import TotTimeStatistic
except ImportError as error:
    print_import_error(__name__, error)


class Filter(DataSource):
    '''
    classdocs
    '''

    def __init__(self, data_source, statistics=None):
        '''
        Constructor
        '''
        DataSource.__init__(self, data_source)
        self.statistics = statistics
        self.statisticsClasses = None
        self.keepAnnotation = False

    @property
    def filter(self):
        statistics = None
        filteredData = None
        if not self.signal == None:
            filteredData = self.__filter__(self.signal, self.annotation)
            if not self.statisticsClasses == None:
                statistics = StatisticsFactory(self.statisticsClasses,
                                               filteredData).statistics
        if self.keepAnnotation:
            filteredData.annotation = self.annotation
        return Filter(filteredData, statistics)

    def __filter__(self, _signal, _annotation=None):
        pass

    def __rrshift__(self, other):
        """ overloading << operator """
        if (isinstance(other, DataSource)):
            self.signal = other.signal
            self.annotation = other.annotation
            return self.filter()

    @property
    def statistics(self):
        return self.__statistics__

    @statistics.setter
    def statistics(self, statistics):
        self.__statistics__ = statistics

    @property
    def statisticsClasses(self):
        return self.__statisticsClasses__

    @statisticsClasses.setter
    def statisticsClasses(self, statistics_classes):
        self.__statisticsClasses__ = statistics_classes

    @property
    def keepAnnotation(self):
        return self.__keepAnnotation__

    @keepAnnotation.setter
    def keepAnnotation(self, _keepAnnotation):
        self.__keepAnnotation__ = _keepAnnotation


class RemoveAnnotatedSignalFilter(Filter):
    def __init__(self, data_source):
        Filter.__init__(self, data_source)
        self.statisticsClasses = (MeanStatistic, SDRRStatistic,
                              NtotStatistic, TotTimeStatistic)

    def __filter__(self, _signal, _annotation):
        if USE_NUMPY_EQUIVALENT:
            return DataSource(_signal[_annotation == 0])

        indexy = find(_annotation == 0)
        indexy = array(indexy)
        _signal = _signal[indexy]
        return DataSource(_signal)


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
        return DataSource(x_p, x_pp)


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
        return DataSource(_signal, _annotation)

    def __numpy_filter__(self, signal, annotation):
        if not self.__leave_annotations__ == (0,):
            annotation[in1d(annotation, self.__leave_annotations__)] = 0
        return DataSource(signal, annotation)
