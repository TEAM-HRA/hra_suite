'''
Created on 24 kwi 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import collections
    import pylab as pl
    from hra_core.io_utils import number_of_lines
except ImportError as error:
    print_import_error(__name__, error)

ALL_ANNOTATIONS = -1

EMPTY_ARRAY = pl.array([])

SignalNoBoundaryAnnotation = \
    collections.namedtuple('SignalNoBoundaryAnnotation',
                           ["signal", "annotation", "annotation_indexes"])


def exclude_boundary_annotations(_signal, _annotation, _excluded_annotations):
    """
    method removes boundary annotations from _annototion array and
    corresponding items from _signal array, returns named tuple
    SignalNoBoundaryAnnotation which includes new signal, new annotation
    array and indexes of remaining annotation values from _annontation
    array; what values are annotations is defined by _excluded_annotations
    parameter
    """
    if _annotation == None or \
        pl.sum(_annotation, dtype=int) == 0:
        return SignalNoBoundaryAnnotation(_signal, _annotation, None)

    #removing nonsinus beats from the beginning
    while (_annotation[0] != 0
            and (_excluded_annotations == ALL_ANNOTATIONS
                 or _annotation[0] in _excluded_annotations)):
        _signal = _signal[1:]
        _annotation = _annotation[1:]
        if len(_signal) == 0:
            break

    if len(_signal) > 0:
        #removing nonsinus beats from the end
        while (_annotation[-1] != 0
            and (_excluded_annotations == ALL_ANNOTATIONS
                or _annotation[-1] in _excluded_annotations)):
            _signal = _signal[:-1]
            _annotation = _annotation[:-1]
            if len(_signal) == 0:
                break

    annotation_indexes = get_annotation_indexes(_annotation,
                                                _excluded_annotations)
    return SignalNoBoundaryAnnotation(_signal, _annotation, annotation_indexes)


def get_annotation_indexes(_annotation, _excluded_annotations):
    """
    method returns indexes of annotation's values in _annotation parameter
    according to annotations defined by _excluded_annotations parameter
    """
    if len(_annotation) == 0:
        return EMPTY_ARRAY
    elif _excluded_annotations == ALL_ANNOTATIONS:
        return pl.array(pl.find(_annotation != 0))
    else:
        #find indexes of annotation array where values are in
        #_excluded_annotations list
        return pl.array(pl.where(
                    pl.in1d(_annotation, _excluded_annotations))[0], dtype=int)


def get_not_annotation_indexes(_annotation, _excluded_annotations):
    """
    method returns indexes of not annotation's values in _annotation parameter,
    annotation values are defined in _excluded_annotations parameter
    """
    if len(_annotation) == 0:
        return EMPTY_ARRAY
    elif _excluded_annotations == ALL_ANNOTATIONS:
        return pl.array(pl.find(_annotation == 0))
    else:
        #find indexes of an annotation array which are NOT included
        #in _excluded_annotations list
        return pl.array(pl.where(pl.logical_not(
                pl.in1d(_annotation, _excluded_annotations)))[0], dtype=int)


def get_unique_annotations(_annotations):
    if _annotations is not None:
        unique_annotations = pl.unique(_annotations)
        return unique_annotations[pl.where(unique_annotations > 0)]


def prepare_data_arrays(_file, _headers_count, _data):
    """
    function creates if necessary array of arrays of data
    """
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
