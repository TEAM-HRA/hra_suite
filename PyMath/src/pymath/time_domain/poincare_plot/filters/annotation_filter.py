'''
Created on 27-07-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import pylab as pl
    from pymath.datasources import DataVector
    from pymath.datasources import ALL_ANNOTATIONS
    from pymath.datasources import exclude_boundary_annotations
    from pymath.datasources import get_not_annotation_indexes
    from pymath.datasources import EMPTY_DATA_VECTOR
    from pymath.time_domain.poincare_plot.filters.filter_utils import Filter
except ImportError as error:
    print_import_error(__name__, error)


class AnnotationFilter(Filter):

    def check(self, _data_vector, _excluded_annotations=ALL_ANNOTATIONS):
        """
        if there are no annotations, a message is returned
        """
        if _data_vector.annotation == None or \
            pl.sum(_data_vector.annotation, dtype=int) == 0:
            return "No annotations found in signal data !"

    def __filter__(self, _data_vector, _excluded_annotations):

        signal_no_boundary_annotations = \
            exclude_boundary_annotations(_data_vector.signal,
                                         _data_vector.annotation,
                                         _excluded_annotations)
        #there is no annotations or all are 0's so nothing changed
        if signal_no_boundary_annotations.annotation_indexes == None:
            return _data_vector

        if len(signal_no_boundary_annotations.signal) > 0:
            signal = signal_no_boundary_annotations.signal
            annotation = signal_no_boundary_annotations.annotation
            indexes_plus = signal_no_boundary_annotations.annotation_indexes
            indexes_minus = indexes_plus - 1
            indexes = pl.r_[indexes_plus, indexes_minus]
            signal_plus = signal[pl.arange(0, len(signal) - self.__shift__)]
            signal_minus = signal[pl.arange(self.__shift__, len(signal))]
            signal_plus[indexes] = -1
            indexes = pl.array(pl.find(signal_plus != -1))
            signal_plus = signal_plus[indexes]
            signal_minus = signal_minus[indexes]

            not_annotation_indexes = get_not_annotation_indexes(
                            _data_vector.annotation, _excluded_annotations)
            signal = _data_vector.signal[not_annotation_indexes]
            annotation = _data_vector.annotation[not_annotation_indexes]
            time = _data_vector.time[not_annotation_indexes] \
                    if _data_vector.time else None

            return DataVector(signal=signal, signal_plus=signal_plus,
                          signal_minus=signal_minus,
                          time=time, annotation=annotation,
                          signal_unit=_data_vector.signal_unit)
        else:  # this happens when all array's elements are filtered out
            return EMPTY_DATA_VECTOR