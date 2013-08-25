'''
Created on 27-03-2013

@author: jurek
'''
from hra.core.special import ImportErrorMessage
try:
    import pylab as pl
    from hra.core.introspection import get_subclasses
    from hra.math.statistics.statistics import Statistic
    from hra.math.statistics.statistics import MeanStatistic
    from hra.math.statistics.statistics import MaxStatistic
    from hra.math.statistics.statistics import MinStatistic
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramStatistic(object):
    """
    marker base class to mark tachogram statistic
    """
    pass


class SignalMeanTachogramStatistic(MeanStatistic, TachogramStatistic):
    @property
    def description(self):
        return 'Mean of signal'


class SignalMinTachogramStatistic(MinStatistic, TachogramStatistic):
    @property
    def description(self):
        return 'Minimum of signal'


class SignalMaxTachogramStatistic(MaxStatistic, TachogramStatistic):
    @property
    def description(self):
        return 'Maximum of signal'


class SignalStandardDeviationTachogramStatistic(Statistic, TachogramStatistic):
    def __calculate__(self):
        return pl.std(self.signal)

    @property
    def description(self):
        return 'Standard deviation of signal'


class AnnotationCountTachogramStatistic(Statistic, TachogramStatistic):
    def __calculate__(self):
        return 0 if self.annotation == None else \
                len(pl.find(self.annotation != 0))

    @property
    def description(self):
        return 'Number of annotations'


class SignalCountTachogramStatistic(Statistic, TachogramStatistic):
    def __calculate__(self):
        return len(self.signal)

    @property
    def description(self):
        return 'Number of signals'


def calculate_tachogram_statistics(**data):
    """
    function to calculate all statistics associated with tachogram plots
    """
    outcomes = {}
    descriptions = {}
    for tachogram_statistic_class in get_subclasses(TachogramStatistic):
        tachogram_statistic = tachogram_statistic_class(**data)
        #remove TachogramStatistic label
        name = tachogram_statistic_class.__name__
        descriptions[name] = tachogram_statistic.description
        outcomes[name] = tachogram_statistic.compute()
    return (outcomes, descriptions, )
