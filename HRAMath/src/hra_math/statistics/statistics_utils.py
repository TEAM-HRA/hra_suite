'''
Created on Sep 1, 2013

@author: jurek
'''
from hra_core.collections_utils import commas
from hra_math.statistics.summary_statistics import \
    expand_to_real_summary_statistics_classes
from hra_math.statistics.statistics import get_statistics_names
from hra_math.statistics.statistics import ALL_STATISTICS
from hra_math.statistics.statistics import CHECK_STATISTICS
from hra_math.statistics.statistics import CORE_STATISTICS
from hra_math.statistics.statistics import ASYMMETRY_STATISTICS
from hra_math.statistics.statistics import NON_CHECK_STATISTICS


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


def available_statistics_info():
    """
    get all available statistics info
    """
    info = []
    for statistic_ident in [CORE_STATISTICS, ASYMMETRY_STATISTICS,
                            CHECK_STATISTICS]:
        info.append(statistic_ident + ': ' +
                   commas(get_statistics_names(statistic_ident)))
    info.append(ALL_STATISTICS + ': all above statistics')
    info.append(NON_CHECK_STATISTICS + ': ' + CORE_STATISTICS + ', '
                + ASYMMETRY_STATISTICS)
