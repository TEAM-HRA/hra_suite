'''
Created on 27-07-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from pycore.introspection import create_class_object_with_suffix
    from pycore.introspection import get_method_arguments_count
    from pymath.time_domain.poincare_plot.filters.filter_utils import expand_to_real_filters_names # @IgnorePep8
    from pymath.time_domain.poincare_plot.filters.filter_utils import get_package_for_filter # @IgnorePep8
except ImportError as error:
    print_import_error(__name__, error)


class FilterManager(object):
    def __init__(self, _shift=1, _excluded_annotations=None, _filters=None):
        self.__filters__ = []
        self.__shift__ = _shift

        if _filters is not None:
            for _filter in _filters:
                if _excluded_annotations and hasattr(_filter,
                                                     'excluded_annotations'):
                    _filter.excluded_annotations = _excluded_annotations
                self.addFilter(_filter)

    def run_filters(self, _data_vector):
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
                data_vector = _filter(data_vector)
        return data_vector

    def addFilter(self, _filter_object_or_handler_or_names):
        """
        filter entity could be passed as filter object itself, handler method
        or a name of filter class
        """
        arg_count = get_method_arguments_count(_filter_object_or_handler_or_names) # @IgnorePep8

        # filter as a string
        if isinstance(_filter_object_or_handler_or_names, str):
            for filter_name in expand_to_real_filters_names(
                                        _filter_object_or_handler_or_names):
                if filter_name == None:
                    return
                _module = get_package_for_filter(filter_name)
                filter_object = create_class_object_with_suffix(
                                    get_package_for_filter(filter_name),
                                    filter_name,
                                    _suffix='Filter')
                filter_object = filter_object(_shift=self.__shift__)
                filter_object.arg_count = -1
                self.__filters__.append(filter_object)
        # filter as a function
        elif arg_count > -1:
            filter_method = _filter_object_or_handler_or_names
            filter_method.arg_count = arg_count
            self.__filters__.append(filter_method)
        # filter as an object
        else:
            filter_object = _filter_object_or_handler_or_names
            filter_object.arg_count = -1
            self.__filters__.append(filter_object)
