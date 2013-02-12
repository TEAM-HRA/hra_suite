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
