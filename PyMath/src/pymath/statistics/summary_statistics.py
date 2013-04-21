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
except ImportError as error:
    print_import_error(__name__, error)

ALL_SUMMARY_STATISTICS = 'ALL'


class SummaryStatisticsFactory(object):
    """
    factory statistics class used for summary statistics that is
    statistics which embrace statistics for the while input data
    """

    def __init__(self, summary_statistics_classes_or_names):
        '''
        Constructor
        '''
        self.__summary_statistics_objects__ = None
        if summary_statistics_classes_or_names == None:
            return
        #if summary_statistics_classes_or_names is a string object which
        #included names of statistics separater by comma we change it into
        #list of names
        if isinstance(summary_statistics_classes_or_names, str):
            summary_statistics_classes_or_names = \
                expand_to_real_summary_statistics_names(summary_statistics_classes_or_names)  # @IgnorePep8

        self.__summary_statistics_objects__ = []
        for type_or_name in summary_statistics_classes_or_names:
            #if type_or_name is a string
            if isinstance(type_or_name, str):
                type_or_name = create_class_object_with_suffix(
                                    'pymath.statistics.summary_statistics',
                                    type_or_name, 'SummaryStatistic')
            #if type_or_name is a class type
            if isinstance(type_or_name, type):
                summary_statistic_object = type_or_name.__new__(type_or_name)
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
            for name, value in \
                [(s1.__class__.__name__, s1.summary_statistic) for s1 in ss]:
                    s_statistics[name[:name.rfind('SummaryStatistic')]] = value
                    return s_statistics

    @property
    def has_summary_statistics(self):
        """
        methods returns True if there are any summary statistics defined
        """
        return 0 if self.__summary_statistics_objects__ == None else \
                len(self.__summary_statistics_objects__) > 0


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


class C1dC1aTimeSummaryStatistic(SummaryStatistic, Asymmetry):
    """
    summary statistic which calculates percentage of time when
    C1d is greater then C1a during processing/moving the window data
    over the whole recording
    """
    def __init__(self):
        self.__summary_time__ = 0
        self.__summary_c1d_time__ = 0
        self.__summary_c1a_time__ = 0

    def calculate(self, statistics, data_vector):
        signal_time = pl.sum(data_vector.signal_plus)
        self.__summary_time__ = self.__summary_time__ + signal_time
        c1d = statistics.get('C1d', None)
        if c1d == None:
            raise ValueError('C1d statistic is required to calculate C1dC1aTimeSummaryStatistic') # @IgnorePep8
        if c1d > 0.5:
            self.__summary_c1d_time__ = self.__summary_c1d_time__ + signal_time

        c1a = statistics.get('C1a', None)
        if c1a == None:
            raise ValueError('C1a statistic is required to calculate C1dC1aTimeSummaryStatistic') # @IgnorePep8        
        if c1a > 0.5:
            self.__summary_c1a_time__ = self.__summary_c1a_time__ + signal_time

    @property
    def summary_statistic(self):
        return self.__summary_c1d_time__ / self.__summary_time__ \
                if self.__summary_time__ > 0 else 0


def get_summary_statistics_names(summary_statistic_ident,
                                 only_short_names=True):
    if summary_statistic_ident == ALL_SUMMARY_STATISTICS:
        names = []
        for _class in [Core]:
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
