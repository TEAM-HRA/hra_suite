'''
Created on 12-02-2013

@author: jurek
'''
import numpy as np


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
    return len(array1) == len(array2) and not np.array_equal(array1, array2)
