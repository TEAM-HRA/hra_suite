'''
Created on 9 kwi 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    from hra_core.collections_utils import remove_suffix
    from hra_core.collections_utils import get_as_list
except ImportError as error:
    print_import_error(__name__, error)

ALL_FILTERS = 'ALL'


def expand_to_real_filters_names(filters_names):
    """
    method converts user's inputed filters names into
    real filters class names
    """
    if filters_names[0] == ALL_FILTERS or filters_names == ALL_FILTERS:
        return get_filters_long_names()
    real_filters_names = []
    real_names = [(real_name, real_name.lower(), ) \
                  for real_name in get_filters_long_names()]
    lower_names = [(name.lower(), name.lower() + 'filter', ) \
                   for name in get_as_list(filters_names)]
    for (filter_lower_name, filter_base_name) in lower_names:
        for (real_name, real_lower_name) in real_names:
            if  real_lower_name in (filter_lower_name, filter_base_name):
                real_filters_names.append(real_name)
                break
        else:
            print('Uknown filter: ' + filter_lower_name)
            return []
    return real_filters_names


def get_filters_subclasses():
    """
    due to difficulty to obtain subclasses of a given class
    when subclasses are placed in different modules,
    all subclasses of Filter class have to be put explicitly
    """
    from hra_math.time_domain.poincare_plot.filters.annotation_filter import AnnotationFilter # @IgnorePep8
    from hra_math.time_domain.poincare_plot.filters.square_filter import SquareFilter # @IgnorePep8    
    return [AnnotationFilter, SquareFilter]


def get_filters_long_names():
    """
    function get class names without package
    """
    return [_class.__name__ for _class in get_filters_subclasses()]


def get_filters_short_names():
    """
    function get class names without package and suffix Filter
    """
    return remove_suffix(get_filters_long_names(), 'Filter')


def get_package_for_filter(filter_name_or_class):
    """
    function get a full class package base on Filter subclass name
    or Filter subclass itself
    """
    for subclass in get_filters_subclasses():
        if subclass == filter_name_or_class or \
            subclass.__name__ == filter_name_or_class:
            return subclass.__module__
