'''
Created on 01-04-2013

@author: jurek
module used to calculate summary statistics that is
statistics which correspond to the whole data recording
'''
from pymath.utils.utils import print_import_error
try:
    import pylab as pl
    from pycore.introspection import create_class_object_with_suffix
    from pycore.introspection import get_subclasses_names_with_suffix
    from pycore.introspection import expand_to_real_class_names
    from pymath.statistics.statistics import C1dStatistic
    from pymath.statistics.statistics import C2dStatistic
    from pymath.statistics.statistics import CdStatistic
    from pymath.statistics.statistics import CountAboveLineIdentityStatistic
    from pymath.statistics.statistics import CountBelowLineIdentityStatistic
    from pymath.statistics.statistics import CaStatistic
    from pymath.statistics.statistics import C1aStatistic
    from pymath.statistics.statistics import C2aStatistic
except ImportError as error:
    print_import_error(__name__, error)

ALL_SUMMARY_STATISTICS = 'ALL'


class SummaryStatisticsFactory(object):
    """
    factory statistics class used for summary statistics that is
    statistics which embrace statistics for the while input data
    """

    def __init__(self, summary_statistics_names=None,
                 summary_statistics_classes=None):
        '''
        Constructor
        '''
        self.__summary_statistics_objects__ = []
        if not summary_statistics_classes == None:
            for summary_statistic_class in summary_statistics_classes:
                self.__summary_statistics_objects__.append(
                                                summary_statistic_class())
        if not summary_statistics_names == None:

            #if summary_statistics_names is a string object which
            #included names of statistics separater by comma we change it into
            #list of names
            if isinstance(summary_statistics_names, str):
                summary_statistics_names = \
                    expand_to_real_summary_statistics_names(
                                                    summary_statistics_names)

            for type_or_name in summary_statistics_names:
                #if type_or_name is a string
                if isinstance(type_or_name, str):
                    type_or_name = create_class_object_with_suffix(
                                        'pymath.statistics.summary_statistics',
                                        type_or_name, 'SummaryStatistic')
                if isinstance(type_or_name, __Inner__):
                    continue
                #if type_or_name is a class type
                if isinstance(type_or_name, type):
                    summary_statistic_object = type_or_name.__new__(type_or_name) # @IgnorePep8
                    summary_statistic_object.__init__()
                    self.__summary_statistics_objects__.append(
                                                    summary_statistic_object)

    def update(self, statistics, data_vector):
        if not self.__summary_statistics_objects__ == None:
            for summary_statistic in self.__summary_statistics_objects__:
                summary_statistic.calculate(statistics, data_vector)

    @property
    def summary_statistics(self):
        if not self.__summary_statistics_objects__ == None:
            ss = self.__summary_statistics_objects__  # alias
            s_statistics = {}
            for _class, value in \
                [(s1.__class__, s1.summary_statistic) for s1 in ss]:
                    s_statistics[_class] = value
            return s_statistics

    @property
    def summary_statistics_for_csv(self):
        """
        method change keys of summary statistics value's dictionary to
        short names of statistics summary classes
        """
        return get_summary_statistics_for_csv(self.summary_statistics)

    @property
    def has_summary_statistics(self):
        """
        methods returns True if there are any summary statistics defined
        """
        return 0 if self.__summary_statistics_objects__ == None else \
                len(self.__summary_statistics_objects__) > 0

    @property
    def summary_statistics_order(self):
        """
        method gives list of ordered of summary statistics classes
        """
        return [statistic_object.__class__
                for statistic_object in self.__summary_statistics_objects__]


class SummaryStatistic(object):
    """
    base class for all summary statistics
    """
    def calculate(self, statistics, data_vector):
        """
        method used to calculate/update summary statistics
        parameter statistics have to be a dictionary of usual statistics,
        data_vector current data vector of poincare plot data window
        """
        pass

    @property
    def summary_statistic(self):
        """
        returns calculated summary statistics
        """
        pass

    @property
    def description(self):
        """
        method which gives ability to append additional statistic's
        description for later use by client code
        """
        return self.__class__.__name__

    @property
    def statistics_dependence(self):
        """
        methods returns statistics on which summary statistic depends
        """
        return None


class __Inner__(object):
    """
    marker class to mark __Inner__ summary statistics,
    usually mark a class as not accessible for outer code
    """
    pass


class Core(object):
    """
    marker class to mark core summary statistics
    """
    pass


class Asymmetry(object):
    """
    marker class to mark asymmetry summary statistics
    """
    pass


def get_summary_statistics_names(summary_statistic_ident,
                                 only_short_names=True):
    if summary_statistic_ident == ALL_SUMMARY_STATISTICS:
        names = []
        for _class in [Asymmetry]:
            names[len(names):] = get_summary_statistics_class_names(_class,
                                        only_short_names=only_short_names)
        return names


def get_summary_statistics_class_names(_class, only_short_names=False):
    """
    method returns names of summary statistics classes
    """
    return get_subclasses_names_with_suffix(_class, only_short_names,
                                     short_name_suffix='SummaryStatistic')


def expand_to_real_summary_statistics_names(statistics_summary_names):
    """
    method converts user's inputed summary statistics names into
    real summary statistics classes names
    """
    names = get_summary_statistics_names(statistics_summary_names, False)
    if not names == None:
        return names

    return expand_to_real_class_names(statistics_summary_names,
                                      SummaryStatistic,
                                      _class_suffix='summarystatistic')


def expand_to_real_summary_statistics_classes(statistics_summary_names):
    """
    function converts user's inputed summary statistics names into
    summary statistics classes
    """
    summary_classes = []
    for summary_class_name in expand_to_real_summary_statistics_names(statistics_summary_names): # @IgnorePep8
        summary_classes.append(eval(summary_class_name + '()').__class__)
    return summary_classes


class __TimeOver50PercentageInnerSummaryStatistic__(SummaryStatistic, __Inner__): # @IgnorePep8
    """
    summary statistic which calculates percentage of time when
    statistic defined by _stat_name last more then 50% of the whole time
    during processing/moving the window data over the whole recording
    """
    def __init__(self, _stat_name):  # , cd_name):
        self.__summary_time__ = 0.0
        self.__summary_stat_time__ = 0.0
        self.__stat_name__ = _stat_name

    def calculate(self, statistics, data_vector):
        self.__summary_time__ = self.__summary_time__ + 1
        stat = statistics.get(self.__stat_name__, None)
        if stat == None:
            raise ValueError(self.__stat_name__ + ' statistic is required to calculate ' + self.__class__.__name__) # @IgnorePep8
        if stat > 0.5:
            self.__summary_stat_time__ = self.__summary_stat_time__ + 1.0
        elif stat < 0.5:
            pass
        else:
            self.__summary_stat_time__ = self.__summary_stat_time__ + 0.5

    @property
    def summary_statistic(self):
        return self.__summary_stat_time__ / self.__summary_time__ \
                if self.__summary_time__ > 0 else 0


class C1aTimeSummaryStatistic(__TimeOver50PercentageInnerSummaryStatistic__, Asymmetry): # @IgnorePep8
    """
    summary statistic which calculates percentage of time when
    C1a is greater then 50% of the whole time during processing/moving
    the window data over the whole recording
    """
    def __init__(self):
        __TimeOver50PercentageInnerSummaryStatistic__.__init__(self, 'C1a')

    @property
    def statistics_dependence(self):
        return [C1aStatistic]


class C2aTimeSummaryStatistic(__TimeOver50PercentageInnerSummaryStatistic__, Asymmetry): # @IgnorePep8
    """
    summary statistic which calculates percentage of time when
    C2a is greater then 50% of the whole time during processing/moving
    the window data over the whole recording
    """
    def __init__(self):
        __TimeOver50PercentageInnerSummaryStatistic__.__init__(self, 'C2a')

    @property
    def statistics_dependence(self):
        return [C2aStatistic]


class C1dTimeSummaryStatistic(__TimeOver50PercentageInnerSummaryStatistic__, Asymmetry): # @IgnorePep8
    """
    summary statistic which calculates percentage of time when
    C1d is greater then 50% of the whole time during processing/moving
    the window data over the whole recording
    """
    def __init__(self):
        __TimeOver50PercentageInnerSummaryStatistic__.__init__(self, 'C1d')

    @property
    def statistics_dependence(self):
        return [C1dStatistic]


class C2dTimeSummaryStatistic(__TimeOver50PercentageInnerSummaryStatistic__, Asymmetry): # @IgnorePep8
    """
    summary statistic which calculates percentage of time when
    C2d is greater then 50% of the whole time during processing/moving
    the window data over the whole recording
    """
    def __init__(self):
        __TimeOver50PercentageInnerSummaryStatistic__.__init__(self, 'C2d')

    @property
    def statistics_dependence(self):
        return [C2dStatistic]

class CdTimeSummaryStatistic(__TimeOver50PercentageInnerSummaryStatistic__, Asymmetry): # @IgnorePep8
    """
    summary statistic which calculates percentage of time when
    Cd is greater then 50% of the whole time during processing/moving
    the window data over the whole recording
    """
    def __init__(self):
        __TimeOver50PercentageInnerSummaryStatistic__.__init__(self, 'Cd')

    @property
    def statistics_dependence(self):
        return [CdStatistic]


class CaTimeSummaryStatistic(__TimeOver50PercentageInnerSummaryStatistic__, Asymmetry): # @IgnorePep8
    """
    summary statistic which calculates percentage of time when
    Ca is greater then 50% of the whole time during processing/moving
    the window data over the whole recording
    """
    def __init__(self):
        __TimeOver50PercentageInnerSummaryStatistic__.__init__(self, 'Ca')

    @property
    def statistics_dependence(self):
        return [CaStatistic]


class AboveBelowDifferenceSummaryStatistic(SummaryStatistic,  Asymmetry):
    """
    summary statistic which computes difference in amount of points
    below and above line of identity
    """
    def __init__(self):
        self.__summary_difference__ = 0

    def calculate(self, statistics, data_vector):
        stat_below = statistics.get('CountBelowLineIdentity', None)
        if stat_below == None:
            raise ValueError('CountBelowLineIdentity statistic is required to calculate AboveBelowDifferenceSummaryStatistic') # @IgnorePep8
        stat_above = statistics.get('CountAboveLineIdentity', None)
        if stat_above == None:
            raise ValueError('CountAboveLineIdentity statistic is required to calculate AboveBelowDifferenceSummaryStatistic') # @IgnorePep8        
        if stat_above > stat_below:
            self.__summary_difference__ = self.__summary_difference__ + 1
        else:
            self.__summary_difference__ = self.__summary_difference__ - 1

    @property
    def summary_statistic(self):
        return self.__summary_difference__

    @property
    def statistics_dependence(self):
        return [CountBelowLineIdentityStatistic,
                CountAboveLineIdentityStatistic]


class __MeanInnerSummaryStatistic__(SummaryStatistic, __Inner__):
    """
    inner summary mean statistic
    """
    def __init__(self, _stat_name):
        self.__stat_name__ = _stat_name
        self.__sum_stat__ = 0.0
        self.__count__ = 0

    def calculate(self, statistics, data_vector):
        stat = statistics.get(self.__stat_name__, None)
        if stat == None:
            raise ValueError(self.__stat_name__ + ' statistic is required to calculate ' + self.__class__.__name__) # @IgnorePep8
        self.__sum_stat__ = self.__sum_stat__ + stat
        self.__count__ = self.__count__ + 1

    @property
    def summary_statistic(self):
        return self.__sum_stat__ / self.__count__


class C1dMeanSummaryStatistic(__MeanInnerSummaryStatistic__, Asymmetry):
    """
    summary mean statistic for C1d
    """
    def __init__(self):
        __MeanInnerSummaryStatistic__.__init__(self, 'C1d')

    @property
    def statistics_dependence(self):
        return [C1dStatistic]


class C2dMeanSummaryStatistic(__MeanInnerSummaryStatistic__, Asymmetry):
    """
    summary mean statistic for C2d
    """
    def __init__(self):
        __MeanInnerSummaryStatistic__.__init__(self, 'C2d')

    @property
    def statistics_dependence(self):
        return [C2dStatistic]


class CdMeanSummaryStatistic(__MeanInnerSummaryStatistic__, Asymmetry):
    """
    summary mean statistic for Cd
    """
    def __init__(self):
        __MeanInnerSummaryStatistic__.__init__(self, 'Cd')

    @property
    def statistics_dependence(self):
        return [CdStatistic]


def get_summary_statistics_for_csv(summary_statistics):
    """
    method change keys of summary statistics value's dictionary to
    short names of statistics summary classes
    """
    statistics = {}
    for _class, value in summary_statistics.items():
        statistics[_class.__name__[:-len('SummaryStatistic')]] = value
    return statistics


def get_summary_statistics_order_for_csv(summary_statistics_classes_order):
    """
    method returns short names of summary statistics in specified order
    """
    if not summary_statistics_classes_order == None:
        return [summary_statistic_class.__name__[:-len('SummaryStatistic')]
            for summary_statistic_class in summary_statistics_classes_order]
