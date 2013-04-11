'''
Created on 9 kwi 2013

@author: jurek
'''

from pymath.utils.utils import print_import_error
try:
    from pycore.collections_utils import commas
    from pycore.collections_utils import get_as_list
    from pycore.introspection import get_subclasses_names
    from pymath.datasources import ALL_ANNOTATIONS
except ImportError as error:
    print_import_error(__name__, error)

ALL_FILTERS = 'ALL'


def getFiltersShortNames():
    """
    to get default filter names; subclasses of Filter class
    """
    return commas(Filter.getSubclassesShortNames())


def expand_to_real_filters_names(filters_names):
    """
    method converts user's inputed filters names into
    real filters class names
    """
    if filters_names[0] == ALL_FILTERS or filters_names == ALL_FILTERS:
        return Filter.getSubclassesLongNames()
    real_filters_names = []
    real_names = [(real_name, real_name.lower(), ) \
                  for real_name in Filter.getSubclassesLongNames()]
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


class Filter(object):
    '''
    base class (in a role of abstract class) for filters
    '''

    def __init__(self, _shift=1, **params):
        '''
        Constructor
        '''
        self.__shift__ = _shift

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    def check(self, _data_vector, _excluded_annotations=ALL_ANNOTATIONS):
        """
        method returns None if a filter will be used or a text message
        if not be used due to specific data conditions
        """
        pass

    def filter(self, _data_vector, _excluded_annotations=ALL_ANNOTATIONS):
        return self.__filter__(_data_vector, _excluded_annotations)

    def __filter__(self, _data_vector, _excluded_annotations):
        return _data_vector

    @staticmethod
    def getSubclassesShortNames():
        return get_subclasses_names(Filter, remove_name='Filter')

    @staticmethod
    def getSubclassesLongNames():
        return get_subclasses_names(Filter)
