## @package statistics
#  @author jurek
#  @date 27-07-2012
#  Classes with base functionality for statistics
from pymath.utils.utils import print_import_error
try:
    import pylab as pl
    from pycore.collections_utils import get_as_list
    from pycore.introspection import create_class_object_with_suffix
    from pycore.introspection import get_method_arguments_count
    from pycore.introspection import get_subclasses_short_names
    from pycore.introspection import get_subclasses
    from pymath.datasources import DataVector
except ImportError as error:
    print_import_error(__name__, error)

USE_IDENTITY_LINE = True


## Base class for all specific statitistics,
#  this class have to be treated as an abstract class for such statistics
class Statistic(DataVector):

    ## Constructor
    #  @param **data
    def __init__(self, **data):
        DataVector.__init__(self, **data)

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
            self.__pre_calculate__()
            value = self.__calculate__()
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
                if str(subclass).find('InnerStatistic') == -1]

    @staticmethod
    def getSubclassesShortNames():
        return [name for name in get_subclasses_short_names(Statistic)
                if name.find('InnerStatistic') == -1]

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None


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
            mean_plus = MeanStatistic(signal=self.signal_plus).compute()
            mean_minus = MeanStatistic(signal=self.signal_minus).compute()
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
        nochange_indexes = pl.find(self.signal_minus == self.signal_plus)
        mean_plus = MeanStatistic(signal=self.signal_plus).compute()
        mean_minus = MeanStatistic(signal=self.signal_minus).compute()
        sd2 = (self.signal_plus - mean_plus
                   + self.signal_minus - mean_minus) / pl.sqrt(2)
        return pl.sqrt((pl.sum(sd2[self.indexes(sd2)] ** 2)
                + (pl.sum(sd2[nochange_indexes] ** 2) / 2)) / pl.size(sd2))

    def indexes(self, sd2):
        return None


class SD2aStatistic(SD2InnerStatistic):
    """
    for accelerations
    """
    def indexes(self, sd2):
        return pl.find(sd2 > 0)


class SD2dStatistic(SD2InnerStatistic):
    """
    for decelerations
    """
    def indexes(self, sd2):
        return pl.find(sd2 < 0)


class SDNNStatistic(Statistic):
    def __calculate__(self):
        global USE_IDENTITY_LINE
        if USE_IDENTITY_LINE:
            SDNNa = SDNNaStatistic(signal_plus=self.signal_plus,
                                    signal_minus=self.signal_minus).compute()
            SDNNd = SDNNdStatistic(signal_plus=self.signal_plus,
                                    signal_minus=self.signal_minus).compute()
            return pl.sqrt(SDNNa ** 2 + SDNNd ** 2)
        else:
            return pl.sqrt(pl.var(self.signal))


class SDNNaStatistic(Statistic):
    """
    for accelerations
    """
    def __calculate__(self):
        SD1a = SD1aStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        SD2a = SD2aStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        return pl.sqrt((SD1a ** 2 + SD2a ** 2) / 2)


class SDNNdStatistic(Statistic):
    """
    for decelerations
    """
    def __calculate__(self):
        SD1d = SD1dStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        SD2d = SD2dStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        return pl.sqrt((SD1d ** 2 + SD2d ** 2) / 2)


class C1aStatistic(Statistic):
    """
    for accelerations
    """
    def __calculate__(self):
        SD1a = SD1aStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        SD1 = SD1Statistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        return (SD1a / SD1) ** 2


class C1dStatistic(Statistic):
    """
    for decelerations
    """
    def __calculate__(self):
        SD1d = SD1dStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        SD1 = SD1Statistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        return (SD1d / SD1) ** 2


class C2aStatistic(Statistic):
    """
    for accelerations
    """
    def __calculate__(self):
        SD2a = SD2aStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        SD2 = SD2Statistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        return (SD2a / SD2) ** 2


class C2dStatistic(Statistic):
    """
    for decelerations
    """
    def __calculate__(self):
        SD2d = SD2dStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        SD2 = SD2Statistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        return (SD2d / SD2) ** 2


class CaStatistic(Statistic):
    """
    for accelerations
    """
    def __calculate__(self):
        SDNNa = SDNNaStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        SDNN = SDNNStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        return (SDNNa / SDNN) ** 2


class CdStatistic(Statistic):
    """
    for decelerations
    """
    def __calculate__(self):
        SDNNd = SDNNdStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        SDNN = SDNNStatistic(signal_plus=self.signal_plus,
                               signal_minus=self.signal_minus).compute()
        return (SDNNd / SDNN) ** 2


class SsStatistic(Statistic):
    def __calculate__(self):
        sd1 = SD1Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus).compute()
        sd2 = SD2Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus).compute()
        return pl.pi * sd1 * sd2


class SD21Statistic(Statistic):
    def __calculate__(self):
        sd1 = SD1Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus).compute()
        sd2 = SD2Statistic(signal_plus=self.signal_plus,
                           signal_minus=self.signal_minus).compute()
        return sd2 / sd1


class ShortAsymmetryStatistic(Statistic):
    def __calculate__(self):
        C1a = C1aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus).compute()
        C1d = C1dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus).compute()
        return 1 if C1d > C1a else 0


class LongAsymmetryStatistic(Statistic):
    def __calculate__(self):
        C2a = C2aStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus).compute()
        C2d = C2dStatistic(signal_plus=self.signal_plus,
                            signal_minus=self.signal_minus).compute()
        return 1 if C2d < C2a else 0


class StatisticsFactory(object):

    def __init__(self, statistics_classes_or_names, statistics_handlers=None,
                 _use_identity_line=True):
        '''
        Constructor
        '''
        self.__statistics_classes__ = []
        self.__statistics_handlers__ = statistics_handlers
        self.__use_identity_line__ = _use_identity_line
        global USE_IDENTITY_LINE
        USE_IDENTITY_LINE = self.__use_identity_line__

        #if statistics_classes_or_names is a string object which included
        #names of statistics separater by comma we change it into list of names
        if isinstance(statistics_classes_or_names, str):
            statistics_classes_or_names = get_as_list(
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
        with StatisticsFactory(self.statistics_classes,
                statistics_handlers=self.__statistics_handlers__,
                _use_identity_line=self.__use_identity_line__) as factory:
            for statistic in factory.statistics_objects:
                statistic.data = _data
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
