'''
Created on 27-07-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from numpy import array
    from numpy import logical_not
    from numpy import where
    from numpy import sum
    from pylab import find
    from pylab import arange
    from pylab import r_
    from pylab import in1d
    from pycore.collections_utils import get_as_list
    from pycore.introspection import create_class_object_with_suffix
    from pycore.introspection import get_method_arguments_count
    from pycore.introspection import get_subclasses_short_names
    from pymath.datasources import DataVector
except ImportError as error:
    print_import_error(__name__, error)


ALL_ANNOTATIONS = 1


class FilterManager(object):
    def __init__(self):
        self.__filters__ = []
        self.__shift__ = 1

    def addFilter(self, _filter_object_or_handler_or_name,
                  _excluded_annotations=ALL_ANNOTATIONS):
        """
        filter entity could be passed as filter object itself, handler method
        or a name of filter class
        """
        if isinstance(_filter_object_or_handler_or_name, str):
            _filter_object_or_handler_or_name = \
                create_class_object_with_suffix(
                        'pymath.time_domain.poincare_plot.filters',
                        _filter_object_or_handler_or_name)
        _filter_object_or_handler_or_name.arg_count = \
            get_method_arguments_count(_filter_object_or_handler_or_name)

        # means this is a object
        if _filter_object_or_handler_or_name.arg_count == -1:
            _filter_object_or_handler_or_name = \
                _filter_object_or_handler_or_name(_excluded_annotations,
                                                  _shift=self.__shift__)
        else:
            _filter_object_or_handler_or_name.excluded_annotations = \
                                _excluded_annotations

        self.__filters__.append(_filter_object_or_handler_or_name)

    def filter(self, _data_vector):
        """
        method which runs all filters as objects or as methods;
        when a method has two parameters it returns two values also
        when has a one parameter it returns one value
        when none parameters none value has to be returned
        """
        data_vector = _data_vector
        for _filter in self.__filters__:
            if _filter.arg_count == -1:
                data_vector = _filter.filter(data_vector)
            else:
                data_vector = _filter(data_vector,
                                      _filter.excluded_annotations)
        return data_vector

    def addFiltersByNames(self, _filters_names):
        if _filters_names is None:
            return
        #an example: AnnotationFilter[1-2-3] or AnnotationFilter
        for filter_part in map(str.strip, _filters_names.split(',')):
            idx_start = filter_part.find('[')
            idx_stop = filter_part.find(']')
            filter_name = \
                filter_part[:(None if idx_start == -1 else idx_start)]
            excluded_annotations = get_as_list(
                        filter_part[idx_start + 1:idx_stop], separator='-') \
                        if idx_start >= 0 and idx_stop > idx_start else None
            if excluded_annotations == None or \
                excluded_annotations == ALL_ANNOTATIONS:
                self.addFilter(filter_name)
            else:
                self.addFilter(filter_name, excluded_annotations)

    def shift(self, _shift):
        self.__shift__ = _shift


class DataVectorFilter(object):
    '''
    classdocs
    '''

    def __init__(self, _excluded_annotations=ALL_ANNOTATIONS, _shift=1):
        '''
        Constructor
        '''
        self.__excluded_annotations__ = _excluded_annotations
        self.__shift__ = _shift

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    def filter(self, _data_vector):
        if self.__excluded_annotations__ == None:
            self.__excluded_annotations__ = ALL_ANNOTATIONS
        return self.__filter__(_data_vector,
                               self.__excluded_annotations__)

    def __filter__(self, _data_vector, _excluded_annotations):
        pass

    @staticmethod
    def getSubclassesShortNames():
        return get_subclasses_short_names(DataVectorFilter,
                                          remove_base_classname=False)


class AnnotationFilter(DataVectorFilter):
    def __filter__(self, _data_vector, _excluded_annotations):

        if _data_vector.annotation == None or \
            sum(_data_vector.annotation, dtype=int) == 0:
            return _data_vector

        signal = _data_vector.signal
        annotation = _data_vector.annotation

        #removing nonsinus beats from the beginning
        while (annotation[0] != 0
                and (_excluded_annotations == ALL_ANNOTATIONS
                     or annotation[0] in _excluded_annotations)):
            signal = signal[1:]
            annotation = annotation[1:]

        #removing nonsinus beats from the end
        while (annotation[-1] != 0
                and (_excluded_annotations == ALL_ANNOTATIONS
                    or annotation[-1] in _excluded_annotations)):
            signal = signal[0:-1]
            annotation = annotation[0:-1]

        if _excluded_annotations == ALL_ANNOTATIONS:
            indexy_p = array(find(annotation != 0))
        else:
            #find indexes of annotation array where values are in
            #_excluded_annotations list
            indexy_p = array(
                where(in1d(annotation, _excluded_annotations))[0], dtype=int)

        indexy_m = indexy_p - 1
        indexy = r_[indexy_p, indexy_m]
        x_p = signal[arange(0, len(signal) - self.__shift__)]
        x_pp = signal[arange(self.__shift__, len(signal))]
        x_p[indexy] = -1
        indexy = array(find(x_p != -1))
        x_p = x_p[indexy]
        x_pp = x_pp[indexy]

        not_annotation_indexes = self.__not_annotation_indexes__(
                            _data_vector.annotation, _excluded_annotations)
        signal = _data_vector.signal[not_annotation_indexes]
        time = _data_vector.time[not_annotation_indexes] \
                if _data_vector.time else None

        return DataVector(signal=signal, signal_plus=x_p, signal_minus=x_pp,
                          time=time, annotation=annotation,
                          signal_unit=_data_vector.signal_unit)

    def __not_annotation_indexes__(self, _annotation, _excluded_annotations):
        if _excluded_annotations == ALL_ANNOTATIONS:
            indexes = array(find(_annotation == 0))
        else:
            #find indexes of an annotation array which are NOT included
            #in _excluded_annotations list
            indexes = array(where(logical_not(in1d(_annotation,
                                    _excluded_annotations)))[0], dtype=int)

        return indexes
