'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from pycore.collections_utils import commas
    from pymath.statistics.statistics import get_statistics_names
    from pymath.statistics.statistics import ALL_STATISTICS
    from pymath.statistics.statistics import CHECK_STATISTICS
    from pymath.statistics.statistics import CORE_STATISTICS
    from pymath.statistics.statistics import ASYMMETRY_STATISTICS
    from pymath.statistics.statistics import NON_CHECK_STATISTICS
except ImportError as error:
    print_import_error(__name__, error)


class StatisticParameters(object):
    """
    parameters concerning statistics
    """
    def __init__(self):
        pass

    @property
    def statistics_names(self):
        """
        [optional]
        names of statistics to be calculated (separated by ','),
        or ALL for all statistics or CHECK for check statistics
        or ASYMMETRY for asymmetry statistics;
        an example: 'mean, sd1, sd2a'
        to get a list of available statistics names call a method:
        available_statistics()
        """
        return self.__statistics_names__

    @statistics_names.setter
    def statistics_names(self, _statistics_names):
        self.__statistics_names__ = _statistics_names

    @property
    def summary_statistics_names(self):
        """
        [optional]
        names of summary_statistics to be calculated (separated by ','),
        or ALL for all summary statistics
        to get a list of available statistics names call a method:
        available_statistics()
        """
        return self.__summary_statistics_names__

    @summary_statistics_names.setter
    def summary_statistics_names(self, _summary_statistics_names):
        self.__summary_statistics_names__ = _summary_statistics_names

    def available_statistics(self):
        """
        [optional]
        print all available statistics names
        """
        for statistic_ident in [CORE_STATISTICS, ASYMMETRY_STATISTICS,
                                CHECK_STATISTICS]:
            print(statistic_ident + ': ' +
                       commas(get_statistics_names(statistic_ident)))
        print(ALL_STATISTICS + ': all above statistics')
        print(NON_CHECK_STATISTICS + ': ' + CORE_STATISTICS + ', '
               + ASYMMETRY_STATISTICS)

    def addStatistic(self, _handler, _name):
        """
        [optional]
        add a statistic function (or handler) with optional _name
        all parameters of this function are type of numpy.array;
        parameter _name is a name of a column in an outcome file associated
        with this statistic function,
        the function could have the following signatures:
            <function name>(signal)
            <function name>(signal, annotation)
            <function name>(signal, signal_plus, signal_minus)
            <function name>(signal, signal_plus, signal_minus, annotation)
        -----------------------------------------------------------------------
        commentary:
        signal - the whole data signal (or part of it)
        annotation - annotation data correspond to signal data
        signal_plus - part of the signal data which corresponds to RRi(n)
        signal_minus - part of the signal data which corresponds to RRi(n+1)
        """
        if self.__statistics_handlers__ == None:
            self.__statistics_handlers__ = []
        _handler.name = _name
        self.__statistics_handlers__.append(_handler)

    def removeStatistic(self, _name):
        """
        [optional]
        remove statistic handler/function associated with a _name
        """
        for idx, _handler in enumerate(self.__statistics_handlers__):
            if _handler.name == _name:
                del self.__statistics_handlers__[idx]
                return

    def setProperties(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'statistics_names', self.statistics_names)
        setattr(_object, 'summary_statistics_names',
                self.summary_statistics_names)
