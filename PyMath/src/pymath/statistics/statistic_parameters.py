'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from pycore.collections_utils import commas
    from pycore.collections_utils import is_empty
    from pymath.model.core_parameters import CoreParameters
    from pymath.statistics.statistics import get_statistics_names
    from pymath.statistics.statistics import ALL_STATISTICS
    from pymath.statistics.statistics import CHECK_STATISTICS
    from pymath.statistics.statistics import CORE_STATISTICS
    from pymath.statistics.statistics import ASYMMETRY_STATISTICS
    from pymath.statistics.statistics import NON_CHECK_STATISTICS
    from pymath.statistics.summary_statistics import expand_to_real_summary_statistics_classes # @IgnorePep8
except ImportError as error:
    print_import_error(__name__, error)


class StatisticParameters(CoreParameters):
    """
    parameters concerning statistics
    """

    NAME = "statistic_parameters"

    def __init__(self):
        self.__statistics_handlers__ = []
        self.__statistics_classes__ = []

        self.__summary_statistics_classes__ = []

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

    def addStatisticHandler(self, _handler, _name):
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

    def removeStatisticHandler(self, _name):
        """
        [optional]
        remove statistic handler/function associated with a _name
        """
        for idx, _handler in enumerate(self.__statistics_handlers__):
            if _handler.name == _name:
                del self.__statistics_handlers__[idx]
                return

    def setObjectStatisticParameters(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'statistics_names', self.statistics_names)
        setattr(_object, 'statistics_classes', self.statistics_classes)
        setattr(_object, 'statistics_handlers', self.statistics_handlers)

        setattr(_object, 'summary_statistics_names', self.summary_statistics_names) # @IgnorePep8
        setattr(_object, 'summary_statistics_classes', self.summary_statistics_classes) # @IgnorePep8

    @property
    def statistics_handlers(self):
        return self.__statistics_handlers__

    @property
    def summary_statistics_classes(self):
        return self.__summary_statistics_classes__

    @summary_statistics_classes.setter
    def summary_statistics_classes(self, _summary_statistics_classes):
        self.__summary_statistics_classes__ = _summary_statistics_classes

    def clearSummaryStatisticsClasses(self):
        self.__summary_statistics_classes__ = []

    @property
    def statistics_classes(self):
        return self.__statistics_classes__

    @statistics_classes.setter
    def statistics_classes(self, _statistics_classes):
        self.__statistics_classes__ = _statistics_classes

    def validateStatisticParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL): # @IgnorePep8
        if is_empty(self.statistics_names) and \
            is_empty(self.statistics_classes) and \
            is_empty(self.statistics_handlers) and \
            is_empty(self.summary_statistics_names) and \
            is_empty(self.summary_statistics_classes):
            return "Statistics names or classes or handlers are required"

    def clearStatisticsClasses(self):
        self.__statistics_classes__ = []


def extended_statistics_classes(_statistics_classes,
                                _statistics_names,
                                _summary_statistics_classes,
                                _summary_statistics_names):
    """
    method extends statistics classes by dependence statistics
    from summary statistics classes o summary statistics names
    """
    if _summary_statistics_names and _statistics_names == None:
        _summary_statistics_classes = \
            expand_to_real_summary_statistics_classes(
                                                _summary_statistics_names)
    if _statistics_classes == None or _summary_statistics_classes == None:
        return _statistics_classes
    statistics_classses = []
    statistics_classses[:] = _statistics_classes
    if len(_summary_statistics_classes) > 0:
        for summary_statistic_class in _summary_statistics_classes:
            summary_statistic = summary_statistic_class()
            for statistic_class in summary_statistic.statistics_dependence:
                if statistics_classses.count(statistic_class) == 0:
                    statistics_classses.append(statistic_class)
    return statistics_classses
