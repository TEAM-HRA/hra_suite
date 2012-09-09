'''
Created on 27-07-2012

@author: jurek
'''

from med.base_statistics.statistics import StatisticsFactory
from med.base_statistics.statistics import Statistic
from med.base_statistics.statistics import SD1Statistic
from med.base_statistics.statistics import SD2Statistic
from med.base_statistics.statistics import SsStatistic
from med.base_statistics.statistics import SD21Statistic
from med.base_statistics.statistics import RStatistic
from med.base_statistics.statistics import RMSSDStatistic
from med.base_statistics.statistics import SD1upStatistic
from med.base_statistics.statistics import SD1downStatistic
from med.base_statistics.statistics import NupStatistic
from med.base_statistics.statistics import NdownStatistic
from med.base_statistics.statistics import NonStatistic

from med.data_sources.datasources import DataSource


class SymmetryStatistic(Statistic):
    def __calculate__(self):
        return 1 if ((self >> SD1upStatistic())
                     > (self >> SD1downStatistic())) else 0


class PoincarePlot(StatisticsFactory):
    '''
    classdocs
    '''

    def __init__(self, data_source=None):
        statistics_classes = (
                            # MeanStatistic,
                            # SDStatistic,
                            # SDRRStatistic,
                            # NtotStatistic,
                            SD1Statistic,
                            SD2Statistic,
                            SsStatistic,
                            SD21Statistic,
                            RStatistic,
                            RMSSDStatistic,
                            SD1upStatistic,
                            SD1downStatistic,
                            NupStatistic,
                            NdownStatistic,
                            NonStatistic,
                            SymmetryStatistic)
        StatisticsFactory.__init__(self, statistics_classes,
                                   data_source=data_source)

    def __rrshift__(self, other):
        if (isinstance(other, DataSource)):
            self.signal = other.signal
            self.annotation = other.annotation
            return self.statistics

#    @staticmethod
#    def poincareOld(__signal__, annotation, filtering):
#        if filtering == 1:
#            filtered_signal = Filter.filter(__signal__, annotation)
#            x_p, x_pp = Filter.pfilter(__signal__, annotation)
#        else:
#            x_p = __signal__[arange(0, len(__signal__) - 1)]
#            x_pp = __signal__[arange(1, len(__signal__))]
#            filtered_signal = __signal__
#
#        RR_mean = Statistics.Mean(filtered_signal)
#        sdrr = Statistics.SDRR(filtered_signal)
#        rmssd = Statistics.RMSSD(x_p, x_pp)
#        sd1 = Statistics.SD1(x_p, x_pp)
#        sd2 = Statistics.SD2(x_p, x_pp)
#        sd21 = Statistics.SD21(x_p, x_pp)
#        s = Statistics.Ss(x_p, x_pp)
#        r = Statistics.R(x_p, x_pp)
#        sd1up = Statistics.SD1up(x_p, x_pp)
#        sd1down = Statistics.SD1down(x_p, x_pp)
#        nup = Statistics.Nup(x_p, x_pp)
#        ndown = Statistics.Ndown(x_p, x_pp)
#        non = Statistics.Non(x_p, x_pp)
#        ntot = Statistics.N_tot(filtered_signal)
#        tot_time = sum(filtered_signal) / (1000 * 60)
#        asym = 0
#        if sd1up > sd1down:
#            asym = 1
#        return RR_mean, sdrr, rmssd, sd1, sd2, sd21, s, r, sd1up, sd1down,
#            asym, nup, ndown, non, ntot, tot_time


class PoincarePlotSegmenter(object):

    def __init__(self, data_source, window_size,  shift=1):
        self.data_source = data_source
        self.__size__ = window_size
        self.__shift__ = shift
        self.__index__ = 0
        if self.__size__ > len(self.data_source.signal):
            raise Exception('Poincare window size greater then signal size !!!') #@IgnorePep8

    def __iter__(self):
        return self

    def next(self):
        if self.__index__ + self.__size__ <= len(self.data_source.signal):
            indexes = range(self.__index__, self.__index__ + self.__size__)
            signal = self.data_source.signal.take(indexes)
            annotation = (None if self.data_source.annotation == None else
                          self.data_source.annotation.take(indexes))

            self.__index__ += self.__shift__

            return DataSource(signal, annotation)
        else:
            raise StopIteration

    @property
    def data_source(self):
        return self.__data_source__

    @data_source.setter
    def data_source(self, _data_source):
        self.__data_source__ = _data_source
