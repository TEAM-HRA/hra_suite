'''
Created on Dec 1, 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import pylab as pl
    from hra_core.io_utils import number_of_lines
except ImportError as error:
    print_import_error(__name__, error)


def prepare_data_arrays(_file, _headers_count, _data):
    """
    function creates if necessary array of arrays of data
    used in file datasource classes
    """
    if _data.ndim == 0:  # this happens when an array holds only one value
        _data = pl.array([_data])
    if _data.ndim == 1:
        #if there is only one line of data (exclude headers lines)
        #we have to convert this array into array of arrays
        #consists of elements of input array, that is:
        #[2, 5, 9, 18]  => [[2], [5], [9], [18]]
        #this step is required because elements of _data
        #have to be arrays themselves not simple numerical types
        if number_of_lines(_file) - _headers_count == 1:
            _data = pl.array([pl.array([_d]) for _d in _data])

    #it is needed to return always 2 dimensional array of data
    #but if data contains only one column then 1 dimensional array
    #would be returned, that's why the following code is required
    return pl.array([_data]) if _data.ndim == 1 else _data
