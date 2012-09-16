'''
Created on 27-07-2012

@author: jurek
'''


from pylab import sqrt
from pylab import size
from pylab import pi
from pylab import dot
from pylab import greater
from pylab import compress
from pylab import equal
from numpy import var

from med.data_sources.datasources import DataSource
from med.globals.globals import *  # @UnusedWildImport


class StaticticsFactory(object):

    def __init__(self, data_source, statistic_classes):
        self.__data_source__ = data_source
        self.__statistic_classes__ = statistic_classes
        self.__statistics__ = []

    def __enter__(self):
        self.__getStatistics__(self.__statistic_classes__)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def statistics(self):
        return self.__statistics__

    def __getStatistics__(self, classes__):
        for class__ in classes__:
            statistic = class__.__new__(class__)
            statistic.__init__(self.__data_source__)
            if (hasattr(self.__data_source__, 'annotation')
                and hasattr(statistic, 'annotation')):
                statistic.annotation = self.__data_source__.annotation
            self.__statistics__.append(statistic)

            #calculate for next level subclasses
            #Warning: this functionality is deactivated
            #self.__getStatistics__(class__)


class Statistic(DataSource):
    '''
    classdocs
    '''

    def __init__(self, data_source=None):
        '''
        Constructor
        '''
        DataSource.__init__(self, data_source)

    def __pre_calculate__(self):
        pass

    def __calculate__(self):
        """ statistic implementation method """
        pass

    def compute(self):
        self.__pre_calculate__()
        value = self.__calculate__()
        return value

    @property
    def id(self):
        name = self.__class__.__name__
        #remove suffix Statistic
        idx = name.find('Statistic')
        return None if idx == -1 else name[:idx]

    def __rrshift__(self, other):
        if (isinstance(other, DataSource)):
            self.signal = other.signal
            self.annotation = other.annotation
            return self.compute()


class MeanStatistic(Statistic):
    '''
    classdocs
    '''

    def __calculate__(self):
        return sum(self.signal) / float(size(self.signal))


class TotTimeStatistic(Statistic):
    '''
    classdocs
    '''

    def __calculate__(self):
        return sum(self.signal) / (1000 * 60)


class SDStatistic(Statistic):
    def __calculate__(self):
        if NUMPY_USAGE:
            return sqrt(var(self.signal, ddof=1))  # ddof=1 means divide by size-1 @IgnorePep8
        else:
            meanValue = MeanStatistic(self.signal).compute()
            return sqrt(sum(((self.signal - meanValue) ** 2))
                        / (size(self.signal) - 1))


class SDRRStatistic(SDStatistic):
    pass


class NtotStatistic(Statistic):
    def __calculate__(self):
        return size(self.signal) - 1


class SD1Statistic(SDStatistic):
    def __pre_calculate__(self):
        self.signal = (self.signal - self.annotation) / sqrt(2)


class SD2Statistic(SDStatistic):
    def __pre_calculate__(self):
        self.signal = (self.signal + self.annotation) / sqrt(2)


class SsStatistic(Statistic):
    def __calculate__(self):
        sd1 = SD1Statistic(self).compute()
        sd2 = SD2Statistic(self).compute()
        return pi * sd1 * sd2


class SD21Statistic(Statistic):
    def __calculate__(self):
        sd1 = SD1Statistic(self).compute()
        sd2 = SD2Statistic(self).compute()
        return sd2 / sd1


class RStatistic(Statistic):
    def __calculate__(self):
        x_pn = self.signal - MeanStatistic(self.signal).compute()
        x_ppn = (self.annotation
                    - MeanStatistic(self.annotation).compute())
        return dot(x_pn, x_ppn) / (sqrt(dot(x_pn, x_pn) * dot(x_ppn, x_ppn)))


class RMSSDStatistic(Statistic):
    def __calculate__(self):
        mean = MeanStatistic((self.signal - self.annotation) ** 2).compute()
        return sqrt(mean)


class SD1upStatistic(Statistic):
    def __calculate__(self):
        xrzut = (self.signal - self.annotation) / sqrt(2)
        nad = compress(greater(0, xrzut), xrzut)
        value = sqrt(sum(nad ** 2) / (size(xrzut) - 1))
        return value


class SD1downStatistic(Statistic):
    def __calculate__(self):
        xrzut = (self.signal - self.annotation) / sqrt(2)
        pod = compress(greater(xrzut, 0), xrzut)
        value = sqrt(sum(pod ** 2) / (size(xrzut) - 1))
        return value


class NupStatistic(Statistic):
    def __calculate__(self):
        xrzut = self.signal - self.annotation
        nad = compress(greater(0, xrzut), xrzut)
        return (size(nad))


class NdownStatistic(Statistic):
    def __calculate__(self):
        xrzut = self.signal - self.annotation
        pod = compress(greater(xrzut, 0), xrzut)
        return (size(pod))


class NonStatistic(Statistic):
    def __calculate__(self):
        xrzut = self.signal - self.annotation
        na = compress(equal(xrzut, 0), xrzut)
        return (size(na))


class StatisticsFactory(DataSource):

    def __init__(self, statistics_classes, data_source=None):
        '''
        Constructor
        '''
        DataSource.__init__(self, data_source)
        self.__statistics_classes__ = statistics_classes

    @property
    def statistics(self):
        __statistics = {}
        with StaticticsFactory(self, self.__statistics_classes__) as factory:
            for statistic in factory.statistics:
                __statistics[statistic.id] = self >> statistic
        return __statistics


#def Mean(__signal__):
#    return sum(__signal__) / float(size(__signal__))


#def SD(__signal__):
#    return sqrt(sum(((__signal__
#            - Mean(__signal__)) ** 2)) / (size(__signal__) - 1))


#def SDRR(__signal__):
#    return SD(__signal__)


#def N_tot(x):
#    return size(x) - 1

#def SD1(__signal__, shifted_data):
#    return SD((__signal__ - shifted_data) / sqrt(2))


#def SD2(__signal__, shifted_data):
#    return SD((__signal__ + shifted_data) / sqrt(2))


#def Ss(__signal__, shifted_data):
#    return pi * SD1(__signal__, shifted_data) * SD2(__signal__, shifted_data)


#def SD21(__signal__, shifted_data):
#    return SD2(__signal__, shifted_data) / SD1(__signal__, shifted_data)


#def R(__signal__, shifted_data):
#    x_pn = __signal__ - Mean(__signal__)
#    x_ppn = shifted_data - Mean(shifted_data)
#    return dot(x_pn, x_ppn) / (sqrt(dot(x_pn, x_pn) * dot(x_ppn, x_ppn)))


#def RMSSD(__signal__, shifted_data):
#    return sqrt(Mean((__signal__ - shifted_data) ** 2))


#def SD1up(__signal__, shifted_data):
#    xrzut = (__signal__ - shifted_data) / sqrt(2)
#    nad = compress(greater(0, xrzut), xrzut)
#    return sqrt(sum(nad ** 2) / (size(xrzut) - 1))


#def SD1down(__signal__, shifted_data):
#    xrzut = (__signal__ - shifted_data) / sqrt(2)
#    pod = compress(greater(xrzut, 0), xrzut)
#    return sqrt(sum(pod ** 2) / (size(xrzut) - 1))


#def Nup(x_p, x_pp):
#    xrzut = x_p - x_pp
#    nad = compress(greater(0, xrzut), xrzut)
#    return (size(nad))


#def Ndown(x_p, x_pp):
#    xrzut = x_p - x_pp
#    pod = compress(greater(xrzut, 0), xrzut)
#    return (size(pod))


#def Non(x_p, x_pp):
#    xrzut = x_p - x_pp
#    na = compress(equal(xrzut, 0), xrzut)
#    return (size(na))
