## @package statistics
#  @author jurek
#  @date 27-07-2012
#  Classes with base functionality for statistics
from hra_math.utils.utils import print_import_error
try:
    import pylab as pl
    import numpy as np
    from hra_core.collections_utils import nvl
    from hra_core.introspection import create_class_object_with_suffix
    from hra_core.introspection import get_subclasses_names_with_suffix
    from hra_core.introspection import get_method_arguments_count
    from hra_core.introspection import get_subclasses_names
    from hra_core.introspection import expand_to_real_class_names
    from hra_math.model.data_vector import DataVector
except ImportError as error:
    print_import_error(__name__, error)

USE_IDENTITY_LINE = True
CORE_STATISTICS = 'CORE'
ALL_STATISTICS = 'ALL'
CHECK_STATISTICS = 'CHECK'
ASYMMETRY_STATISTICS = 'ASYMMETRY'
NON_CHECK_STATISTICS = 'NON_CHECK'


def get_statistics_names(statistic_ident, only_short_names=True):
    if statistic_ident == ALL_STATISTICS:  # means without Inner
        names = []
        for _class in [Core, Asymmetry, Check]:
            names[len(names):] = get_statistics_class_names(_class,
                                        only_short_names=only_short_names)
        return names
    if statistic_ident == NON_CHECK_STATISTICS:  # means without Inner, Check
        names = []
        for _class in [Core, Asymmetry]:
            names[len(names):] = get_statistics_class_names(_class,
                                        only_short_names=only_short_names)
        return names
    elif statistic_ident == CHECK_STATISTICS:
        return get_statistics_class_names(Check,
                                          only_short_names=only_short_names)
    elif statistic_ident == ASYMMETRY_STATISTICS:
        return get_statistics_class_names(Asymmetry,
                                          only_short_names=only_short_names)
    elif statistic_ident == CORE_STATISTICS:
        return get_statistics_class_names(Core,
                                          only_short_names=only_short_names)


def expand_to_real_statistics_names(statistics_names):
    """
    method converts user's inputed statistics names into
    real statistics class names
    """
    names = get_statistics_names(statistics_names, False)
    if not names == None:
        return names

    return expand_to_real_class_names(statistics_names, Statistic,
                                      _class_suffix='statistic')


## Base class for all specific statitistics,
#  this class have to be treated as an abstract class for such statistics
class Statistic(DataVector):

    ## Constructor
    #  @param **data
    def __init__(self, **data):
        DataVector.__init__(self, **data)
        self.__buffer__ = data.get('buffer')
        self.__buffer_name__ = data.get('buffer_name', '')

    ## Method (optional) to put pre calculations done before proper
    #  calculations
    def __pre_calculate__(self):
        pass

    ## Method which have to be implemented in a derived class and
    #  it have to contain all proper calculations
    def __calculate__(self):
        pass

    ## Method used by clients to get a calculated value of specific statistic
    #  @return calculated value of a statistic
    def compute(self):
        if self.handler:
            if self.handler.arg_count == 2:
                return self.handler(self.signal, self.annotation)
            elif self.handler.arg_count == 1:
                return self.handler(self.signal)
            elif self.handler.arg_count == 3:
                return self.handler(self.signal, self.signal_plus,
                                    self.signal_minus)
            elif self.handler.arg_count == 4:
                return self.handler(self.signal, self.signal_plus,
                                    self.signal_minus, self.annotation)
            return self.handler()
        else:
            value = self.buffer.get(self.__class__.__name__
                                    + self.buffer_name) \
                    if not self.buffer == None else None
            if value == None:
                self.__pre_calculate__()
                value = self.__calculate__()
                if not self.buffer == None:
                    self.buffer[self.__class__.__name__
                                + self.buffer_name] = value
            return value

    ## Method used to get a name of a statistic based on derived statistic's
    #  class name
    #  @return the name, of statistic, which doesn't contain word Statistic
    @property
    def _id(self):
        if self.name:
            return self.name
        name = self.__class__.__name__
        #remove suffix Statistic
        idx = name.find('Statistic')
        return None if idx == -1 else name[:idx]

    def __rrshift__(self, other):
        #depreciated method
        raise NotImplementedError("def Statistic.__rrshift__(self, other)")

    @property
    def name(self):
        return self.__name__

    @name.setter
    def name(self, _name):
        self.__name__ = _name

    @property
    def handler(self):
        return self.__handler__

    @handler.setter
    def handler(self, _handler):
        if _handler:
            #name of a handler is a name of statistic
            self.name = getattr(_handler, 'name', None)
            if self.name is None:
                self.name = locals().get('_handler').__name__
            self.__handler__ = _handler
            #add number of arguments of a handler
            self.__handler__.arg_count = \
                            get_method_arguments_count(self.__handler__)

    @staticmethod
    def getSubclassesShortNames():
        return [name for name in get_subclasses_names(Statistic,
                                                remove_base_classname=True)]

    @staticmethod
    def getSubclassesLongNames():
        return [name for name in get_subclasses_names(Statistic)]

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    @property
    def buffer(self):
        return self.__buffer__

    @buffer.setter
    def buffer(self, _buffer):
        self.__buffer__ = _buffer

    @property
    def buffer_name(self):
        return self.__buffer_name__

    @buffer_name.setter
    def buffer_name(self, _buffer_name):
        self.__buffer_name__ = _buffer_name

    @property
    def description(self):
        """
        method which gives ability to append additional statistic's
        description for later use by client code
        """
        return self.__class__.__name__


class Asymmetry(object):
    """
    marker class to mark asymmetry statistic
    """
    pass


class Check(object):
    """
    marker class to mark check statistic
    """
    pass


class Core(object):
    """
    marker class to mark core statistic
    """
    pass


class Inner(object):
    """
    marker class to mark Inner statistic
    """
    pass


def get_statistics_class_names(_class, only_short_names=False):
    """
    method returns names of statistics classes
    """
    return get_subclasses_names_with_suffix(_class, only_short_names,
                                     short_name_suffix='Statistic')


class MeanStatistic(Statistic, Core):
    '''
    classdocs
    '''
    def __calculate__(self):
        return pl.mean(self.signal)


class MeanPlusStatistic(Statistic, Core):
    def __calculate__(self):
        return MeanStatistic(signal=self.signal_plus).compute()


class MeanMinusStatistic(Statistic, Core):
    def __calculate__(self):
        return MeanStatistic(signal=self.signal_minus).compute()


class SD1Statistic(Statistic, Asymmetry):
    def __calculate__(self):
        global USE_IDENTITY_LINE
        sd1 = (self.signal_plus - self.signal_minus) / pl.sqrt(2)
        if USE_IDENTITY_LINE:
            return pl.sqrt(pl.sum((sd1 ** 2)) / len(self.signal_plus))
        else:
            return pl.sqrt(pl.var(sd1))


class SD1InnerStatistic(Statistic, Inner):
    def __calculate__(self):
        global USE_IDENTITY_LINE
        if USE_IDENTITY_LINE:
            sd1 = (self.signal_plus - self.signal_minus) / pl.sqrt(2)
        else:
            mean_plus = MeanStatistic(signal=self.signal_plus,
                                      buffer=self.buffer,
                                      buffer_name='plus').compute()
            mean_minus = MeanStatistic(signal=self.signal_minus,
                                       buffer=self.buffer,
                                       buffer_name='minus').compute()
            sd1 = (self.signal_plus - mean_plus
                   - self.signal_minus + mean_minus) / pl.sqrt(2)
        return pl.sqrt(pl.sum(sd1[self.indexes(sd1)] ** 2) / pl.size(sd1))

    def indexes(self, sd1):
        return None


class SD1aStatistic(SD1InnerStatistic, Asymmetry):
    """
    for accelerations
    """
    def indexes(self, sd1):
        return pl.find(sd1 > 0)


class SD1dStatistic(SD1InnerStatistic, Asymmetry):
    """
    for decelerations
    """
    def indexes(self, sd1):
        return pl.find(sd1 < 0)


class SD2Statistic(Statistic, Asymmetry):
    def __calculate__(self):
        sd2 = (self.signal_plus + self.signal_minus) / pl.sqrt(2)
        return pl.sqrt(pl.var(sd2))


class SD2InnerStatistic(Statistic, Inner):
    def __calculate__(self):

        mean_plus = MeanStatistic(signal=self.signal_plus,
                                  buffer=self.buffer,
                                  buffer_name='plus').compute()
        mean_minus = MeanStatistic(signal=self.signal_minus,
                                  buffer=self.buffer,
                                  buffer_name='minus').compute()

        #division for acceleration, deceleration or no change points
        #have to be done using sd1 vector
        global USE_IDENTITY_LINE
        if USE_IDENTITY_LINE:
            sd1 = (self.signal_plus - self.signal_minus) / pl.sqrt(2)
        else:
            sd1 = (self.signal_plus - self.signal_minus
                    - mean_plus + mean_minus) / pl.sqrt(2)
        nochange_indexes = pl.find(sd1 == 0)

        sd2 = (self.signal_plus - mean_plus
                   + self.signal_minus - mean_minus) / pl.sqrt(2)
        return pl.sqrt((pl.sum(sd2[self.indexes()] ** 2)
                + (pl.sum(sd2[nochange_indexes] ** 2)) / 2) / pl.size(sd2))

    def indexes(self, sd):
        return None


class SD2aStatistic(SD2InnerStatistic, Asymmetry):
    """
    for accelerations
    """
    def indexes(self):
        return pl.find(self.signal_minus < self.signal_plus)


class SD2dStatistic(SD2InnerStatistic, Asymmetry):
    """
    for decelerations
    """
    def indexes(self):
        return pl.find(self.signal_minus > self.signal_plus)


class SDNNStatistic(Statistic, Asymmetry):
    def __calculate__(self):
        SDNNa = SDNNaStatistic(signal_plus=self.signal_plus,
                                    signal_minus=self.signal_minus,
                                    buffer=self.buffer).compute()
        SDNNd = SDNNdStatistic(signal_plus=self.signal_plus,
                                    signal_minus=self.signal_minus,
                                    buffer=self.buffer).compute()
        return pl.sqrt(SDNNa ** 2 + SDNNd ** 2)


class SDNNaStatistic(Statistic, Asymmetry):
    """
    for accelerations
    """
    def __calculate__(self):
        SD1a = SD1aStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        SD2a = SD2aStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        return pl.sqrt((SD1a ** 2 + SD2a ** 2) / 2)


class SDNNdStatistic(Statistic, Asymmetry):
    """
    for decelerations
    """
    def __calculate__(self):
        SD1d = SD1dStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        SD2d = SD2dStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        return pl.sqrt((SD1d ** 2 + SD2d ** 2) / 2)


class C1aStatistic(Statistic, Asymmetry):
    """
    for accelerations
    """
    def __calculate__(self):
        SD1a = SD1aStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        SD1 = SD1Statistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        return (SD1a / SD1) ** 2


class C1dStatistic(Statistic, Asymmetry):
    """
    for decelerations
    """
    def __calculate__(self):
        SD1d = SD1dStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        SD1 = SD1Statistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        return (SD1d / SD1) ** 2


class C2aStatistic(Statistic, Asymmetry):
    """
    for accelerations
    """
    def __calculate__(self):
        SD2a = SD2aStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        SD2 = SD2Statistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        return (SD2a / SD2) ** 2


class C2dStatistic(Statistic, Asymmetry):
    """
    for decelerations
    """
    def __calculate__(self):
        SD2d = SD2dStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        SD2 = SD2Statistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        return (SD2d / SD2) ** 2


class CaStatistic(Statistic, Asymmetry):
    """
    for accelerations
    """
    def __calculate__(self):
        SDNNa = SDNNaStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        SDNN = SDNNStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        return (SDNNa / SDNN) ** 2


class CdStatistic(Statistic, Asymmetry):
    """
    for decelerations
    """
    def __calculate__(self):
        SDNNd = SDNNdStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        SDNN = SDNNStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus,
                               buffer=self.buffer).compute()
        return (SDNNd / SDNN) ** 2


class SsStatistic(Statistic, Asymmetry):
    def __calculate__(self):
        sd1 = SD1Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus,
                           buffer=self.buffer).compute()
        sd2 = SD2Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus,
                           buffer=self.buffer).compute()
        return pl.pi * sd1 * sd2


class SD21Statistic(Statistic, Asymmetry):
    def __calculate__(self):
        sd1 = SD1Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus,
                           buffer=self.buffer).compute()
        sd2 = SD2Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus,
                           buffer=self.buffer).compute()
        return sd2 / sd1


class SD1AsymmetryStatistic(Statistic, Asymmetry):
    def __calculate__(self):
        C1a = C1aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        C1d = C1dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return 1 if C1d > C1a else 0


class SD2AsymmetryStatistic(Statistic, Asymmetry):
    def __calculate__(self):
        C2a = C2aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        C2d = C2dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return 1 if C2d < C2a else 0


class CCheckStatistic(Statistic, Check):
    """
    statistic check if Ca + Cd == 1
    """
    def __calculate__(self):
        Ca = CaStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        Cd = CdStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return Cd + Ca - 1


class C1CheckStatistic(Statistic, Check):
    """
    statistic check if C1a + C1d == 1
    """
    def __calculate__(self):
        C1a = C1aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        C1d = C1dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return C1d + C1a - 1


class C2CheckStatistic(Statistic, Check):
    """
    statistic check if C2a + C2d == 1
    """
    def __calculate__(self):
        C2a = C2aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        C2d = C2dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return C2d + C2a - 1


class SD1CheckStatistic(Statistic, Check):
    """
    statistic check if SD1^2 == SD1a^2 + SD1d^2
    """
    def __calculate__(self):
        SD1 = SD1Statistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD1a = SD1aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD1d = SD1dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return SD1 ** 2 - SD1a ** 2 - SD1d ** 2


class SD2CheckStatistic(Statistic, Check):
    """
    statistic check if SD2^2 == SD2a^2 + SD2d^2
    """
    def __calculate__(self):
        SD2 = SD2Statistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD2a = SD2aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD2d = SD2dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return SD2 ** 2 - SD2a ** 2 - SD2d ** 2


class SDNNCheckStatistic(Statistic, Check):
    """
    statistic check if SDNN^2 == SDNNa^2 + SDNNd^2
    """
    def __calculate__(self):
        SDNN = SDNNStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SDNNa = SDNNaStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SDNNd = SDNNdStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return SDNN ** 2 - SDNNa ** 2 - SDNNd ** 2


class SDNNaCheckStatistic(Statistic, Check):
    """
    statistic check if SDNNa^2 == (SD1a^2 + SD2a^2)/2
    """
    def __calculate__(self):
        SDNNa = SDNNaStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD1a = SD1aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD2a = SD2aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return SDNNa ** 2 - (SD1a ** 2 + SD2a ** 2) / 2


class SDNNdCheckStatistic(Statistic, Check):
    """
    statistic check if SDNNd^2 == (SD1d^2 + SD2d^2)/2
    """
    def __calculate__(self):
        SDNNd = SDNNdStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD1d = SD1dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD2d = SD2dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return SDNNd ** 2 - (SD1d ** 2 + SD2d ** 2) / 2


class MaxStatistic(Statistic, Core):
    '''
    classdocs
    '''
    def __calculate__(self):
        return np.max(self.signal)


class MinStatistic(Statistic, Core):
    '''
    classdocs
    '''
    def __calculate__(self):
        return np.min(self.signal)


class SDRRStatistic(Statistic, Core):
    """
    calculate variance of the hole signal
    """
    def __calculate__(self):
        return pl.sqrt(pl.var(self.signal, ddof=0))


class CSStatistic(Statistic, Asymmetry):
    """
    calculate statistic SD1^2/(2SDNN^2)
    """
    def __calculate__(self):
        SD1 = SD1Statistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SDNN = SDNNStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return (SD1 ** 2) / (2 * (SDNN ** 2))


class SD2SD1Statistic(Statistic, Asymmetry):
    """
    calculate statistic SD2/SD1
    """
    def __calculate__(self):
        SD1 = SD1Statistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD2 = SD2Statistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return SD2 / SD1


class SD2dSD1dStatistic(Statistic, Asymmetry):
    """
    calculate statistic sd2d/sd1d
    """
    def __calculate__(self):
        SD1d = SD1dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD2d = SD2dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return SD2d / SD1d


class SD2aSD1aStatistic(Statistic, Asymmetry):
    """
    calculate statistic sd2a/sd1a
    """
    def __calculate__(self):
        SD1a = SD1aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        SD2a = SD2aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return SD2a / SD1a


class C1d50C2d50Statistic(Statistic, Asymmetry):
    """
    calculate statistic C1d > 50 and C2d < 50
    """
    def __calculate__(self):
        C1d = C1dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        C2d = C2dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return C1d > 0.5 and C2d < 0.5


class CountAboveLineIdentityStatistic(Statistic, Asymmetry):
    """
    calculate number of points above line of identity
    """
    def __calculate__(self):
        return len(pl.where(self.signal_minus > self.signal_plus)[0])


class CountBelowLineIdentityStatistic(Statistic, Asymmetry):
    """
    calculate number of points below line of identity
    """
    def __calculate__(self):
        return len(pl.where(self.signal_minus < self.signal_plus)[0])


class StatisticsFactory(object):

    def __init__(self, statistics_names=None, statistics_handlers=None,
                 _use_identity_line=True, use_buffer=True,
                 statistics_classes=None):
        '''
        Constructor
        '''
        self.__statistics_classes__ = statistics_classes \
                                        if statistics_classes else []
        self.__statistics_objects__ = []
        self.__statistics_handlers__ = statistics_handlers
        self.__use_identity_line__ = _use_identity_line
        self.__use_buffer__ = nvl(use_buffer, True)
        global USE_IDENTITY_LINE
        USE_IDENTITY_LINE = self.__use_identity_line__

        #if statistics_names is a string object which included
        #names of statistics separater by comma we change it into list of names
        if not statistics_names == None:
            if isinstance(statistics_names, str):
                statistics_names = expand_to_real_statistics_names(
                                                            statistics_names)

            for type_or_name in statistics_names:
                #if type_or_name is a string
                if isinstance(type_or_name, str):
                    type_or_name = create_class_object_with_suffix(
                                            'hra_math.statistics.statistics',
                                            type_or_name, 'Statistic')
                #if type_or_name is a class type
                if isinstance(type_or_name, type):
                    self.__statistics_classes__.append(type_or_name)

    def statistics(self, _data):
        __statistics = {}
        _buffer = {} if self.__use_buffer__ else None
        with StatisticsFactory(statistics_classes=self.statistics_classes,
                statistics_handlers=self.__statistics_handlers__,
                _use_identity_line=self.__use_identity_line__,
                use_buffer=self.__use_buffer__) as factory:
            for statistic in factory.statistics_objects:
                statistic.data = _data
                statistic.buffer = _buffer
                __statistics[statistic._id] = statistic.compute()
        return __statistics

    @property
    def statistics_classes(self):
        return self.__statistics_classes__

    def __enter__(self):
        self.__generate_statistics_objects__(self.statistics_classes)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def statistics_objects(self):
        return self.__statistics_objects__

    @property
    def has_statistics(self):
        """
        methods returns True if any statistic is set up for use
        by statistics factory
        """
        return len(self.statistics_classes) > 0

    def __generate_statistics_objects__(self, classes__):
        for class__ in classes__:
            statistic_object = class__.__new__(class__)
            statistic_object.__init__()
            self.statistics_objects.append(statistic_object)

        if not self.__statistics_handlers__ == None:
            for handler in self.__statistics_handlers__:
                statistic = Statistic()
                statistic.handler = handler
                self.statistics_objects.append(statistic)

            #calculate for next level subclasses
            #Warning: this functionality is deactivated
            #self.__generate_statistics_objects__(class__)
