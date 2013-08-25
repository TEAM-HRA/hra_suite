'''
Created on 30 maj 2013

@author: jurek
'''
from hra.core.special import ImportErrorMessage
try:
    import pylab as pl
    from hra.math.model.data_vector_accessor import DataVectorAccessor
    from hra.math.model.data_vector import DataVector
except ImportError as error:
    ImportErrorMessage(error, __name__)


class DataVectorsAccessorGroup(object):
    """
    convenient class to group many data vectors accessors objects
    """

    def __init__(self):
        self.__minimal_data_vector_accessor__ = None
        self.__minimal_signal__ = None
        self.__data_vectors_accessors__ = []
        self.__max_signal__ = None
        self.__min_signal__ = None
        self.__unique_annotations__ = set()

    def addDataVectorAccessor(self, data_vector_accessor):
        self.__data_vectors_accessors__.append(data_vector_accessor)

        _sum = pl.sum(data_vector_accessor.signal)
        _min = pl.amin(data_vector_accessor.signal)
        _max = pl.amax(data_vector_accessor.signal)

        if self.__minimal_signal__ == None:
            self.__minimal_signal__ = _sum
            self.__minimal_data_vector_accessor__ = data_vector_accessor

            self.__min_signal__ = _min
            self.__max_signal__ = _max

        if _sum < self.__minimal_signal__:
            self.__minimal_data_vector_accessor__ = data_vector_accessor
            self.__minimal_signal__ = _sum

        if _min < self.__min_signal__:
            self.__min_signal__ = _min

        if _max > self.__max_signal__:
            self.__max_signal__ = _max

        #collects unique annotations (>0) as a set
        if not data_vector_accessor.annotation == None:
            unique_annotations = pl.unique(data_vector_accessor.annotation[
                                pl.where(data_vector_accessor.annotation > 0)])
            if len(unique_annotations) > 0:
                #union of sets
                self.__unique_annotations__ |= set(unique_annotations)

    @property
    def data_vectors_accessors(self):
        return self.__data_vectors_accessors__

    @property
    def group_data_vector_accessor(self):
        """
        group data vector accessor which represents the whole group;
        this data vector accessor is artificially created:
        its length (in signal units) is the same as for a minimal data vector,
        the signal includes min and max value of all signals;
        annotation part of group data vector accessor includes all unique
        annotations spotted in all group's annotations arrays
        """
        minimal_accessor = self.__minimal_data_vector_accessor__

        #create copy of minimal data vector
        data_vector = minimal_accessor.data_vector.copy()

        #sum_signal0 is a sum of a minimal data accessor signal
        #minus min and max values of all data vectors accessors
        #substraction is required to get the same signal length
        #as minimal data vector at the end
        sum_signal0 = pl.sum(data_vector.signal) - \
                    (self.__max_signal__ + self.__min_signal__)

        #calculate how many times mean signal (the mean of max and min values)
        #is contained in sum_signal0
        mean_signal = (self.__max_signal__ + self.__min_signal__) / 2
        means_count = sum_signal0 / mean_signal

        #create a signal as a array of means plus min and max values
        #to get the same signal length as minimal data vector
        group_signal = means_count * [mean_signal]
        group_signal.insert(0, self.__min_signal__)
        group_signal.append(self.__max_signal__)

        #create annotation part of group data signal
        group_annotation = len(group_signal) * [0]
        if len(self.__unique_annotations__) > 0:
            #it doesn't matter which positions are annotated
            #so the first are marked as annotated
            for idx, value in enumerate(self.__unique_annotations__):
                group_annotation[idx] = value

        group_annotation = pl.array(group_annotation)
        group_signal = pl.array(group_signal)

        group_data_vector = DataVector(signal=group_signal,
                                       annotation=group_annotation,
                                       signal_unit=data_vector.signal_unit)
        group_data_vector_accessor = DataVectorAccessor(group_data_vector)

        #group data vector accessor must have the same listeners
        #as normal minimal data vector accessor to be properly used
        #in process of statistics calculation
        group_data_vector_accessor.listeners = minimal_accessor.listeners
        group_data_vector_accessor.signal_x_unit = minimal_accessor.signal_x_unit  # @IgnorePep8

        return group_data_vector_accessor
