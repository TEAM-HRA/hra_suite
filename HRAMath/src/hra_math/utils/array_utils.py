'''
Created on 12-02-2013

@author: jurek
'''
import numpy as np
from hra_core.datetime_utils import convert_strings_to_datetimes
from hra_core.datetime_utils import get_miliseconds_from_timedelta


def get_max_index_for_cumulative_sum_greater_then_value(_array, value,
                                                     start_index=0):
    """
    this function returns the first index of _array calculated from
    cumulative sum of values of _array where cumulative sum value is >= then
    passed value; searched indexes starts at start_index position
    """
    indexes = range(start_index, len(_array))
    sub_array = _array.take(indexes)
    cumulative_array = np.cumsum(sub_array)
    indexes = np.where(cumulative_array >= value)[0]
    return indexes[0] + start_index if len(indexes) > 0 else -1


def get_max_index_for_cumulative_sum_of_means_greater_then_value(_array, _value): # @IgnorePep8
    """
    this function returns the first index of array calculated as array of
    mean values of the parameter _array at position where cumulative sum
    of the calculated array is grater or equal then parameter _value
    """
    mean_array = np.array([np.mean(_array)] * len(_array))
    return get_max_index_for_cumulative_sum_greater_then_value(mean_array,
                                                               _value)

#test code
if __name__ == '__main__':
    a = np.array([1, 2, 1, 3, 2, 1, 2, 3, 2, 1, 1, 2])
    print(str(get_max_index_for_cumulative_sum_of_means_greater_then_value(a, 7)))  # @IgnorePep8


def arrays_equal(array1, array2):
    """
    function checks if two numpy arrays are equal
    """
    return len(array1) == len(array2) and np.array_equal(array1, array2)


def array_copy(_array):
    """
    returns copy of array parameter
    """
    return None if _array == None else _array.copy()


def get_datetimes_array_as_miliseconds_intervals(datetimes, _format):
    """
    function converts array of datetime strings into milisecond intervals,
    datatime items are parsed acccording to _format parameter;
    (assumption: it is assumed that datetimes are beginning of intervals)
    an example:
    input array (could be any iterable, including numpy array):
    ["08:21:44.020", "08:21:44.870", "08:21:45.550",
                         "08:21:45.900", "08:21:46.333"]

    output array (numpy array):
    [850 <=> ("08:21:44.870" - "08:21:44.020"),
     680 <=> ("08:21:45.550" - "08:21:44.870"),
     350 <=> ("08:21:45.900" - "08:21:45.550"),
     433 <=> ("08:21:46.333" - "08:21:45.900")]

    important note:
    output array has a size less by one as compared to input array,
    there is no equivalent in the output array of the last item
    of the input array, because there is no end time for the last item
    """
    if not datetimes == None and len(datetimes) > 0:
        if isinstance(datetimes[0], str):
            datetimes = np.array(
                            convert_strings_to_datetimes(datetimes, _format))

        #a difference between two arrays (which gives in this case
        #numpy array of timedelta objects) utilizes numpy functionality;
        #that is why this function has to use numpy and be placed in this
        #module instead of some general purpose module
        miliseconds = map(get_miliseconds_from_timedelta,
                                             datetimes[1:] - datetimes[:-1])

        return np.array(miliseconds)
    return datetimes if isinstance(datetimes, np.array) \
                        else np.array(datetimes)
