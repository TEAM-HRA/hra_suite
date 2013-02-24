'''
Created on 27-07-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import pylab as pl
    from pycore.collections_utils import nvl
    from pycore.introspection import create_class_object_with_suffix
    from pycore.introspection import get_method_arguments_count
    from pycore.introspection import get_subclasses_short_names
    from pymath.datasources import DataVector
    from pymath.datasources import ALL_ANNOTATIONS
    from pymath.datasources import exclude_boundary_annotations
    from pymath.datasources import get_not_annotation_indexes
except ImportError as error:
    print_import_error(__name__, error)


class FilterManager(object):
    def __init__(self, _shift=1, _excluded_annotations=ALL_ANNOTATIONS,
                 _filters=None):
        self.__filters__ = []
        self.__shift__ = _shift
        self.__excluded_annotations__ = nvl(_excluded_annotations,
                                            ALL_ANNOTATIONS)

        if _filters is not None:
            for (_filter, excluded_annotation) in _filters:
                self.addFilter(_filter, nvl(excluded_annotation,
                                            ALL_ANNOTATIONS))

    def filter(self, _data_vector):
        """
        method which runs all filters as objects or as methods;
        when a method has two parameters it returns two values also
        when has a one parameter it returns one value
        when none parameters none value has to be returned
        """
        data_vector = _data_vector
        for _filter in self.__filters__:
            excluded_annotations = getattr(_filter, 'excluded_annotations',
                                           self.__excluded_annotations__)
            if _filter.arg_count == -1:
                data_vector = _filter.filter(data_vector, excluded_annotations)
            else:
                data_vector = _filter(data_vector, excluded_annotations)
        return data_vector

    def addFilter(self, _filter_object_or_handler_or_name,
                                        _excluded_annotations=ALL_ANNOTATIONS):
        """
        filter entity could be passed as filter object itself, handler method
        or a name of filter class
        """
        if _excluded_annotations == None:
            _excluded_annotations = ALL_ANNOTATIONS
        arg_count = get_method_arguments_count(_filter_object_or_handler_or_name) # @IgnorePep8

        # filter as a string
        if isinstance(_filter_object_or_handler_or_name, str):
            filter_object = create_class_object_with_suffix(
                                    'pymath.time_domain.poincare_plot.filters',
                                    _filter_object_or_handler_or_name)
            filter_object = filter_object(_shift=self.__shift__)
            filter_object.arg_count = -1
            filter_object.excluded_annotations = _excluded_annotations
            self.__filters__.append(filter_object)
        # filter as a function
        elif arg_count > -1:
            filter_method = _filter_object_or_handler_or_name
            filter_method.arg_count = arg_count
            self.__filters__.append(filter_method)
        # filter as an object
        else:
            filter_object = _filter_object_or_handler_or_name
            filter_object.arg_count = -1
            filter_object.excluded_annotations = _excluded_annotations
            self.__filters__.append(filter_object)


class DataVectorFilter(object):
    '''
    base class (in a role of abstract class) for filters
    '''

    def __init__(self, _shift=1):
        '''
        Constructor
        '''
        self.__shift__ = _shift

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    def filter(self, _data_vector, _excluded_annotations):
        return self.__filter__(_data_vector, _excluded_annotations)

    def __filter__(self, _data_vector, _excluded_annotations):
        return _data_vector

    @staticmethod
    def getSubclassesShortNames():
        return get_subclasses_short_names(DataVectorFilter,
                                          remove_base_classname=False)


class AnnotationFilter(DataVectorFilter):
    def __filter__(self, _data_vector, _excluded_annotations):

        signal_no_boundary_annotations = \
            exclude_boundary_annotations(_data_vector.signal,
                                         _data_vector.annotation,
                                         _excluded_annotations)
        #there is no annotations or all are 0's so nothing changed
        if signal_no_boundary_annotations.annotation_indexes == None:
            return _data_vector

        signal = signal_no_boundary_annotations.signal
        annotation = signal_no_boundary_annotations.annotation

        indexy_p = signal_no_boundary_annotations.annotation_indexes
        indexy_m = indexy_p - 1
        indexy = pl.r_[indexy_p, indexy_m]
        x_p = signal[pl.arange(0, len(signal) - self.__shift__)]
        x_pp = signal[pl.arange(self.__shift__, len(signal))]
        x_p[indexy] = -1
        indexy = pl.array(pl.find(x_p != -1))
        x_p = x_p[indexy]
        x_pp = x_pp[indexy]

        not_annotation_indexes = get_not_annotation_indexes(
                            _data_vector.annotation, _excluded_annotations)
        signal = _data_vector.signal[not_annotation_indexes]
        time = _data_vector.time[not_annotation_indexes] \
                if _data_vector.time else None

        return DataVector(signal=signal, signal_plus=x_p, signal_minus=x_pp,
                          time=time, annotation=annotation,
                          signal_unit=_data_vector.signal_unit)
