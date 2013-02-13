## @package statistics
#  @author jurek
#  @date 27-07-2012
#  Classes with base functionality for statistics
from pymath.utils.utils import print_import_error
try:
    import inspect
    from pylab import sqrt
    from pylab import size
    from pylab import pi
    from pylab import dot
    from pylab import greater
    from pylab import compress
    from pylab import equal
    from numpy import var
    from pycore.units import Minute
    from pycore.collections_utils import get_as_list
    from pycore.introspection import get_class_object
    from pymath.utils.utils import USE_NUMPY_EQUIVALENT
    from pymath.datasources import DataSource
except ImportError as error:
    print_import_error(__name__, error)


## Base class for all specific statitistics,
#  this class have to be treated as an abstract class for such statistics
class Statistic(DataSource):

    ## Constructor
    #  @param **data
    def __init__(self, **data):
        DataSource.__init__(self, **data)

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
                return self.handler(self.signal, self.shifted_signal)
            elif self.handler.arg_count == 1:
                return self.handler(self.signal)
            elif self.handler.arg_count == 3:
                return self.handler(self.signal, self.shifted_signal,
                                    self.annotation)
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
            self.name = locals().get('_handler').__name__
            self.__handler__ = _handler
            #add number of arguments of a handler
            self.__handler__.arg_count = len(
                                    inspect.getargspec(self.__handler__).args)

    @staticmethod
    def getSubclasses():
        return Statistic.__subclasses__()

    @staticmethod
    def getSubclassesShortNames():
        return [_class.__name__[:_class.__name__.rfind('Statistic')]
                for _class in Statistic.getSubclasses()]

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None


class MeanStatistic(Statistic):
    '''
    classdocs
    '''
    def __calculate__(self):
        return sum(self.signal) / float(size(self.signal))


class TotTimeStatistic(Statistic):
    '''
    classdocs
    '''
    def __calculate__(self):
        # total time in minute unit (1000 * 60)
        return sum(self.signal) / Minute.toUnitMultiplier(self.signal_unit)


class SDStatistic(Statistic):
    def __calculate__(self):
        if USE_NUMPY_EQUIVALENT:
            # ddof=1 means divide by size-1
            return sqrt(var(self.signal, ddof=1))
        else:
            meanValue = MeanStatistic(signal=self.signal).compute()
            return sqrt(sum(((self.signal - meanValue) ** 2))
                        / (size(self.signal) - 1))


class SDRRStatistic(SDStatistic):
    pass


class NtotStatistic(Statistic):
    def __calculate__(self):
        return size(self.signal) - 1


class SD1Statistic(SDStatistic):
    def __pre_calculate__(self):
        self.signal = (self.signal - self.shifted_signal) / sqrt(2)


class SD2Statistic(SDStatistic):
    def __pre_calculate__(self):
        self.signal = (self.signal + self.shifted_signal) / sqrt(2)


class SsStatistic(Statistic):
    def __calculate__(self):
        sd1 = SD1Statistic(signal=self.signal,
                           shifted_signal=self.shifted_signal).compute()
        sd2 = SD2Statistic(signal=self.signal,
                           shifted_signal=self.shifted_signal).compute()
        return pi * sd1 * sd2


class SD21Statistic(Statistic):
    def __calculate__(self):
        sd1 = SD1Statistic(signal=self.signal,
                           shifted_signal=self.shifted_signal).compute()
        sd2 = SD2Statistic(signal=self.signal,
                           shifted_signal=self.shifted_signal).compute()
        return sd2 / sd1


class RStatistic(Statistic):
    def __calculate__(self):
        x_pn = self.signal - MeanStatistic(signal=self.signal).compute()
        x_ppn = (self.shifted_signal
                    - MeanStatistic(signal=self.shifted_signal).compute())
        return dot(x_pn, x_ppn) / (sqrt(dot(x_pn, x_pn) * dot(x_ppn, x_ppn)))


class RMSSDStatistic(Statistic):
    def __calculate__(self):
        mean = MeanStatistic(
                signal=(self.signal - self.shifted_signal) ** 2).compute()
        return sqrt(mean)


class SD1upStatistic(Statistic):
    def __calculate__(self):
        xrzut = (self.signal - self.shifted_signal) / sqrt(2)
        nad = compress(greater(0, xrzut), xrzut)
        value = sqrt(sum(nad ** 2) / (size(xrzut) - 1))
        return value


class SD1downStatistic(Statistic):
    def __calculate__(self):
        xrzut = (self.signal - self.shifted_signal) / sqrt(2)
        pod = compress(greater(xrzut, 0), xrzut)
        value = sqrt(sum(pod ** 2) / (size(xrzut) - 1))
        return value


class NupStatistic(Statistic):
    def __calculate__(self):
        xrzut = self.signal - self.shifted_signal
        nad = compress(greater(0, xrzut), xrzut)
        return (size(nad))


class NdownStatistic(Statistic):
    def __calculate__(self):
        xrzut = self.signal - self.shifted_signal
        pod = compress(greater(xrzut, 0), xrzut)
        return (size(pod))


class NonStatistic(Statistic):
    def __calculate__(self):
        xrzut = self.signal - self.shifted_signal
        na = compress(equal(xrzut, 0), xrzut)
        return (size(na))


class SymmetryStatistic(Statistic):
    def __calculate__(self):
        return 1 if SD1upStatistic(signal=self.signal,
                            shifted_signal=self.shifted_signal).compute() > \
                SD1downStatistic(signal=self.signal, \
                        shifted_signal=self.shifted_signal).compute() else 0


class StatisticsFactory(object):

    def __init__(self, statistics_classes_or_names, statistics_handlers=None):
        '''
        Constructor
        '''
        self.__statistics_classes__ = []
        self.__statistics_handlers__ = statistics_handlers

        #if statistics_classes_or_names is a string object which included
        #names of statistics separater by comma we change it into list of names
        if isinstance(statistics_classes_or_names, str):
            statistics_classes_or_names = get_as_list(
                                                statistics_classes_or_names)

        for type_or_name in statistics_classes_or_names:
            #if type_or_name is a string
            if isinstance(type_or_name, str):
                #check if a name is not in dot format
                if not type_or_name.rfind('.') >= 0:
                    #append a 'Statistic' suffix if not present already
                    if not type_or_name.endswith('Statistic'):
                        type_or_name += 'Statistic'
                    #prefix with current package
                    type_or_name = '.'.join(['pymath.statistics.statistics',
                                             type_or_name])
                class_object = get_class_object(type_or_name)
                if class_object == None:
                    raise TypeError("class " + type_or_name + " doesn't exist")
                else:
                    type_or_name = class_object

            #if type_or_name is a class type
            if isinstance(type_or_name, type):
                self.__statistics_classes__.append(type_or_name)
        self.__statistics_objects__ = []

    def statistics(self, _data):
        __statistics = {}
        with StatisticsFactory(self.statistics_classes,
                statistics_handlers=self.__statistics_handlers__) as factory:
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
