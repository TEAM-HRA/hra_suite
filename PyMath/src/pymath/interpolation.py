'''
Created on 03-09-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import pylab as pl
    from itertools import count
    from pymath.utils.utils import USE_NUMPY_EQUIVALENT
    from pymath.datasources import exclude_boundary_annotations
    from pymath.datasources import get_annotation_indexes
    from pymath.datasources import get_not_annotation_indexes
    from pycore.introspection import get_subclasses_names
except ImportError as error:
    print_import_error(__name__, error)


def get_interpolation(_interpolation_class_name):
    """
    returns interpolation object based on _interpolation_class_name parameter
    """
    if _interpolation_class_name:
        try:
            return eval(_interpolation_class_name + '()')
        except NameError:
            print('Warning !!! Interpolation ' + _interpolation_class_name + ' not defined !')  # @IgnorePep8
    return Interpolation()


class InterpolationManager(object):
    def __init__(self, _interpolation_name_or_class):
        if isinstance(_interpolation_name_or_class, str):
            self.__interpolation__ = get_interpolation(
                                            _interpolation_name_or_class)
        else:
            self.__interpolation__ = _interpolation_name_or_class()

    def interpolate(self, _data_vector, _excluded_annotations):
        return self.__interpolation__.interpolate(_data_vector,
                                                  _excluded_annotations)


class Interpolation(object):
    def interpolate(self, _data_vector, _excluded_annotations):
        if _data_vector.signal is not None:
            return self.__interpolate__(_data_vector.signal,
                                        _data_vector.annotation,
                                        _excluded_annotations)
        else:
            return _data_vector.signal

    def __interpolate__(self, _signal, _annotation, _excluded_annotations):
        return _signal

    @staticmethod
    def getSubclassesShortNames():
        return get_subclasses_names(Interpolation)


class LinearInterpolation(Interpolation):
    def __interpolate__(self, _signal, _annotation, _excluded_annotations):
        signal_no_boundary_annotations = \
                        exclude_boundary_annotations(_signal,
                                                     _annotation,
                                                     _excluded_annotations)
        #there is no annotations or all are 0's so nothing changed
        if signal_no_boundary_annotations.annotation_indexes == None:
            return _signal

        index_nonsin = signal_no_boundary_annotations.annotation_indexes
        _signal = signal_no_boundary_annotations.signal

        if USE_NUMPY_EQUIVALENT:
            # artificially appends index of value -1 (by append function)
            # to get the same size of arrays, because idx have to
            # processed all values of idx_nonsin array
            for step, idx, idx_next in zip(count(start=1),
                                           index_nonsin,
                                           pl.append(index_nonsin[1:], -1)):
                if (idx_next - idx) != 1:
                    r = pl.arange(1, step + 1)
                    delta = (_signal[idx + 1] - _signal[idx - step]) / (step + 1) # @IgnorePep8
                    _signal[idx - step + r] = _signal[idx - step] + delta * r
        else:
            krok = 1
            for i in pl.arange(0, len(index_nonsin)):
                if i + 1 <= (len(index_nonsin) - 1) and (index_nonsin[i + 1]
                                                    - index_nonsin[i]) == 1:
                    krok += 1
                else:
                    delta = (_signal[index_nonsin[i] + 1]
                             - _signal[index_nonsin[i] - krok]) / (krok + 1)
                    for k in pl.arange(1, krok + 1):
                        _signal[index_nonsin[i] - krok + k] = _signal[index_nonsin[i] #@IgnorePep8
                                                        - krok] + delta * k
                    krok += 1
        return _signal


class MeanInterpolation(Interpolation):
    def __interpolate__(self, _signal, _annotation, _excluded_annotations):
        sinus_index = get_not_annotation_indexes(_annotation,
                                                _excluded_annotations)

        nonsinus_index = get_annotation_indexes(_annotation,
                                                _excluded_annotations)

        mean_sinus = pl.mean(_signal[sinus_index])
        _signal[nonsinus_index] = mean_sinus
        return _signal
