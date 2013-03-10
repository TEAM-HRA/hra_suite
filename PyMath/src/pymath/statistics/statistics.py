## @package statistics
#  @author jurek
#  @date 27-07-2012
#  Classes with base functionality for statistics
from pymath.utils.utils import print_import_error
try:
    import pylab as pl
    from pycore.collections_utils import nvl
    from pycore.collections_utils import get_as_list
    from pycore.introspection import create_class_object_with_suffix
    from pycore.introspection import get_method_arguments_count
    from pycore.introspection import get_subclasses_short_names
    from pycore.introspection import get_subclasses
    from pymath.datasources import DataVector
except ImportError as error:
    print_import_error(__name__, error)

USE_IDENTITY_LINE = True
ALL_STATISTICS = 'ALL'
CHECK_STATISTICS = 'CHECK'


def expand_to_real_statistics_names(statistics_names):
    """
    method converts user's inputed statistics names into
    real statistics class names
    """
    if statistics_names == ALL_STATISTICS:
        return Statistic.getSubclassesLongNames()
    elif statistics_names == CHECK_STATISTICS:
        return [name for name in Statistic.getSubclassesLongNames()
                if name.endswith('CheckStatistic')]
    real_statistics_names = []
    real_names = [(real_name, real_name.lower(), ) \
                  for real_name in Statistic.getSubclassesLongNames()]
    lower_names = [(name.lower(), name.lower() + 'statistic', ) \
                   for name in get_as_list(statistics_names)]
    for (statistic_lower_name, statistic_base_name) in lower_names:
        for (real_name, real_lower_name) in real_names:
            if  real_lower_name in (statistic_lower_name, statistic_base_name):
                real_statistics_names.append(real_name)
                break
        else:
            print('Uknown statistic: ' + statistic_lower_name)
            return []
    return real_statistics_names


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
    def getSubclasses():
        return [subclass for subclass in get_subclasses(Statistic)
                if not subclass.__name__.endswith('InnerStatistic')]

    @staticmethod
    def getSubclassesShortNames():
        return [name for name in get_subclasses_short_names(Statistic,
                                                    remove_base_classname=True)
                if not name.endswith('Inner')]

    @staticmethod
    def getSubclassesLongNames():
        return [name for name in get_subclasses_short_names(Statistic)
                if not name.endswith('Inner')]

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


class MeanStatistic(Statistic):
    '''
    classdocs
    '''
    def __calculate__(self):
        return pl.mean(self.signal)


class SD1Statistic(Statistic):
    def __calculate__(self):
        global USE_IDENTITY_LINE
        sd1 = (self.signal_plus - self.signal_minus) / pl.sqrt(2)
        if USE_IDENTITY_LINE:
            return pl.sqrt(pl.sum((sd1 ** 2)) / len(self.signal_plus))
        else:
            return pl.sqrt(pl.var(sd1))


class SD1InnerStatistic(Statistic):
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


class SD1aStatistic(SD1InnerStatistic):
    """
    for accelerations
    """
    def indexes(self, sd1):
        return pl.find(sd1 > 0)


class SD1dStatistic(SD1InnerStatistic):
    """
    for decelerations
    """
    def indexes(self, sd1):
        return pl.find(sd1 < 0)


class SD2Statistic(Statistic):
    def __calculate__(self):
        sd2 = (self.signal_plus + self.signal_minus) / pl.sqrt(2)
        return pl.sqrt(pl.var(sd2))


class SD2InnerStatistic(Statistic):
    def __calculate__(self):

        #division for acceleration, deceleration or no change points
        #have to be done using sd1 vector
        sd1 = (self.signal_plus - self.signal_minus) / pl.sqrt(2)
        nochange_indexes = pl.find(sd1 == 0)

        mean_plus = MeanStatistic(signal=self.signal_plus,
                                  buffer=self.buffer,
                                  buffer_name='plus').compute()
        mean_minus = MeanStatistic(signal=self.signal_minus,
                                  buffer=self.buffer,
                                  buffer_name='minus').compute()
        sd2 = (self.signal_plus - mean_plus
                   + self.signal_minus - mean_minus) / pl.sqrt(2)
        return pl.sqrt((pl.sum(sd2[self.indexes(sd1)] ** 2)
                + (pl.sum(sd2[nochange_indexes] ** 2) / 2)) / pl.size(sd2))

    def indexes(self, sd):
        return None


class SD2aStatistic(SD2InnerStatistic):
    """
    for accelerations
    """
    def indexes(self, sd):
        return pl.find(sd > 0)


class SD2dStatistic(SD2InnerStatistic):
    """
    for decelerations
    """
    def indexes(self, sd):
        return pl.find(sd < 0)


class SDNNStatistic(Statistic):
    def __calculate__(self):
        global USE_IDENTITY_LINE
        if USE_IDENTITY_LINE:
            SDNNa = SDNNaStatistic(signal_plus=self.signal_plus,
                                    signal_minus=self.signal_minus,
                                    buffer=self.buffer).compute()
            SDNNd = SDNNdStatistic(signal_plus=self.signal_plus,
                                    signal_minus=self.signal_minus,
                                    buffer=self.buffer).compute()
            return pl.sqrt(SDNNa ** 2 + SDNNd ** 2)
        else:
            return pl.sqrt(pl.var(self.signal))


class SDNNaStatistic(Statistic):
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


class SDNNdStatistic(Statistic):
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


class C1aStatistic(Statistic):
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


class C1dStatistic(Statistic):
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


class C2aStatistic(Statistic):
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


class C2dStatistic(Statistic):
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


class CaStatistic(Statistic):
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


class CdStatistic(Statistic):
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


class SsStatistic(Statistic):
    def __calculate__(self):
        sd1 = SD1Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus,
                           buffer=self.buffer).compute()
        sd2 = SD2Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus,
                           buffer=self.buffer).compute()
        return pl.pi * sd1 * sd2


class SD21Statistic(Statistic):
    def __calculate__(self):
        sd1 = SD1Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus,
                           buffer=self.buffer).compute()
        sd2 = SD2Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus,
                           buffer=self.buffer).compute()
        return sd2 / sd1


class ShortAsymmetryStatistic(Statistic):
    def __calculate__(self):
        C1a = C1aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        C1d = C1dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return 1 if C1d > C1a else 0


class LongAsymmetryStatistic(Statistic):
    def __calculate__(self):
        C2a = C2aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        C2d = C2dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus,
                            buffer=self.buffer).compute()
        return 1 if C2d < C2a else 0


class CCheckStatistic(Statistic):
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


class C1CheckStatistic(Statistic):
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


class C2CheckStatistic(Statistic):
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


class SD1CheckStatistic(Statistic):
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


class SD2CheckStatistic(Statistic):
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


class SDNNCheckStatistic(Statistic):
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


class SDNNaCheckStatistic(Statistic):
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


class SDNNdCheckStatistic(Statistic):
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


class StatisticsFactory(object):

    def __init__(self, statistics_classes_or_names, statistics_handlers=None,
                 _use_identity_line=True, use_buffer=True):
        '''
        Constructor
        '''
        self.__statistics_classes__ = []
        self.__statistics_handlers__ = statistics_handlers
        self.__use_identity_line__ = _use_identity_line
        self.__use_buffer__ = nvl(use_buffer, True)
        global USE_IDENTITY_LINE
        USE_IDENTITY_LINE = self.__use_identity_line__

        #if statistics_classes_or_names is a string object which included
        #names of statistics separater by comma we change it into list of names
        if isinstance(statistics_classes_or_names, str):
            statistics_classes_or_names = expand_to_real_statistics_names(
                                            statistics_classes_or_names)

        for type_or_name in statistics_classes_or_names:
            #if type_or_name is a string
            if isinstance(type_or_name, str):
                type_or_name = create_class_object_with_suffix(
                                                'pymath.statistics.statistics',
                                                type_or_name, 'Statistic')
            #if type_or_name is a class type
            if isinstance(type_or_name, type):
                self.__statistics_classes__.append(type_or_name)
        self.__statistics_objects__ = []

    def statistics(self, _data):
        __statistics = {}
        _buffer = {} if self.__use_buffer__ else None
        with StatisticsFactory(self.statistics_classes,
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

#class SymmetryStatistic(Statistic):
#    def __calculate__(self):
#        SD1a = SD1aStatistic(signal_plus=self.signal_plus,
#                            signal_minus=self.signal_minus).compute()
#        SD1d = SD1dStatistic(signal_plus=self.signal_plus,
#                            signal_minus=self.signal_minus).compute()
#        return 1 if SD1a > SD1d else 0

#class TotTimeStatistic(Statistic):
#    '''
#    classdocs
#    '''
#    def __calculate__(self):
#        # total time in minute unit (1000 * 60)
#        return sum(self.signal) / Minute.expressInUnit(self.signal_unit)
#
#
#class SDStatistic(Statistic):
#    def __calculate__(self):
#        if USE_NUMPY_EQUIVALENT:
#            # ddof=1 means divide by size-1
#            return pl.sqrt(pl.var(self.signal, ddof=1))
#        else:
#            meanValue = MeanStatistic(signal=self.signal).compute()
#            return pl.sqrt(pl.sum(((self.signal - meanValue) ** 2))
#                        / (pl.size(self.signal) - 1))
#
#
#class SDRRStatistic(SDStatistic):
#    pass
#
#
#class NtotStatistic(Statistic):
#    def __calculate__(self):
#        return pl.size(self.signal) - 1
#
#
#class RStatistic(Statistic):
#    def __calculate__(self):
#        x_pn = (self.signal_plus
#                    - MeanStatistic(signal=self.signal_plus).compute())
#        x_ppn = (self.signal_minus
#                    - MeanStatistic(signal=self.signal_minus).compute())
#        return pl.dot(x_pn, x_ppn) / (pl.sqrt(pl.dot(x_pn, x_pn) * pl.dot(x_ppn, x_ppn))) # @IgnorePep8
#
#
#class RMSSDStatistic(Statistic):
#    def __calculate__(self):
#        mean = MeanStatistic(
#                signal=(self.signal_plus - self.signal_minus) ** 2).compute()
#        return pl.sqrt(mean)
#
#
#class NupStatistic(Statistic):
#    def __calculate__(self):
#        xrzut = self.signal_plus - self.signal_minus
#        nad = pl.compress(pl.greater(0, xrzut), xrzut)
#        return (pl.size(nad))
#
#
#class NdownStatistic(Statistic):
#    def __calculate__(self):
#        xrzut = self.signal_plus - self.signal_minus
#        pod = pl.compress(pl.greater(xrzut, 0), xrzut)
#        return (pl.size(pod))
#
#
#class NonStatistic(Statistic):
#    def __calculate__(self):
#        xrzut = self.signal_plus - self.signal_minus
#        na = pl.compress(pl.equal(xrzut, 0), xrzut)
#        return (pl.size(na))

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
