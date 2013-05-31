'''
Created on 30 maj 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import pylab as pl
except ImportError as error:
    ImportErrorMessage(error, __name__)

MINIMAL_GROUP_POLICY = 1


class DataVectorsAccessorGroup(object):
    """
    convenient class to group many data vectors accessors objects
    use to give ability to access a data vector accessor with
    minimal signal duration time
    """

    def __init__(self, group_policy=MINIMAL_GROUP_POLICY):
        self.__group_policy__ = group_policy
        self.__main_data_vector_accessor__ = None
        self.__sum_signal__ = None
        self.__data_vectors_accessors__ = []

    def addDataVectorAccessor(self, data_vector_accessor):
        self.__data_vectors_accessors__.append(data_vector_accessor)
        if self.__sum_signal__ == None:
            self.__sum_signal__ = pl.sum(data_vector_accessor.signal)
            self.__main_data_vector_accessor__ = data_vector_accessor
        if self.__group_policy__ == MINIMAL_GROUP_POLICY:
            if pl.sum(data_vector_accessor.signal) < self.__sum_signal__:
                self.__main_data_vector_accessor__ = data_vector_accessor
                self.__sum_signal__ = pl.sum(data_vector_accessor.signal)

    @property
    def main_data_vector_accessor(self):
        return self.__main_data_vector_accessor__

    @property
    def data_vectors_accessors(self):
        return self.__data_vectors_accessors__
