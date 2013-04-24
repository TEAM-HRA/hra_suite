'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import gc
    import pylab as pl
    from pymath.utils.array_utils import arrays_equal
except ImportError as error:
    print_import_error(__name__, error)


class DataVectorAccessor(object):
    """
    class used to check if there are any changes in data_vector object
    and if this is the case all listeners are called
    """
    def __init__(self, _data_vector):
        # this is the first stage of data
        self.__data_vector0__ = _data_vector
        self.__data_vector__ = self.__data_vector0__.copy()
        self.__data_vector_listeners__ = {}
        # this member represents signal unit for x axis of a plot
        self.__x_signal_unit__ = None

    @property
    def data_vector(self):
        return self.__data_vector__

    @property
    def signal(self):
        return self.__data_vector__.signal

    @property
    def annotation(self):
        return self.__data_vector__.annotation

    @property
    def annotation0(self):
        """
        returns annotations of original state of data
        """
        return self.__data_vector0__.annotation

    @property
    def signal_unit(self):
        return self.__data_vector__.signal_unit

    @property
    def signal_x_unit(self):
        return self.__x_signal_unit__

    @property
    def signal_in_x_unit(self):
        """
        property expresses signal in signal x unit instead of original unit
        """
        if self.signal_unit == self.signal_x_unit:
            return self.signal
        multiplier = self.signal_unit.expressInUnit(self.signal_x_unit)
        return pl.cumsum(self.signal) * multiplier

    def addListener(self, _host, _data_vector_listener):
        self.__data_vector_listeners__[_host] = _data_vector_listener

    def changeSignal(self, _host, _signal, **params):
        if not arrays_equal(self.__data_vector__.signal, _signal):
            self.__data_vector__.signal = _signal
            for host in self.__data_vector_listeners__:
                if not _host == host:  # to avoid recurrence
                    self.__data_vector_listeners__[host].changeSignal(_signal,
                                                                     **params)

    def changeAnnotation(self, _host, _annotation, **params):
        if not arrays_equal(self.__data_vector__.annotation, _annotation):
            self.__data_vector__.annotation = _annotation
            for host in self.__data_vector_listeners__:
                if not _host == host:  # to avoid recurrence
                    self.__data_vector_listeners__[host].changeAnnotation(
                                                        _annotation, **params)

    def changeXSignalUnit(self, _host, _unit, **params):
        if not self.__x_signal_unit__ == _unit:
            self.__x_signal_unit__ = _unit
            for host in self.__data_vector_listeners__:
                if not _host == host:  # to avoid recurrence
                    self.__data_vector_listeners__[host].changeXSignalUnit(
                                                            _unit, **params)

    def restore(self, **params):
        """
        method used to be invoked to restore original state of data vector
        """
        if arrays_equal(self.__data_vector__.signal,
                        self.__data_vector0__.signal) and \
           arrays_equal(self.__data_vector__.annotation,
                         self.__data_vector0__.annotation):
            return
        self.__data_vector__ = None
        gc.collect()  # to force garbage collection
        self.__data_vector__ = self.__data_vector0__.copy()
        for host in self.__data_vector_listeners__:
            self.__data_vector_listeners__[host].changeSignal(
                                    self.__data_vector__.signal, **params)
            self.__data_vector_listeners__[host].changeAnnotation(
                                    self.__data_vector__.annotation, **params)
