'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from pycore.collections_utils import get_as_list
    from pymath.time_domain.poincare_plot.filters.filter_utils import get_filters_short_names # @IgnorePep8
except ImportError as error:
    print_import_error(__name__, error)


class FilterParameters(object):
    """
    parameters concerning filters
    """
    def __init__(self):
        self.__filters__ = []

    def available_filters(self):
        """
        [optional]
        print all available filters names
        """
        print(get_filters_short_names())

    @property
    def filters_names(self):
        """
        [optional]
        use filters names (separated by comma)
        to get list of standard filters names call a function:
        get_filters_short_names()
        [module: pymath.time_domain.poincare_plot.poincare_plot]
        """
        return self.__filters_names__

    @filters_names.setter
    def filters_names(self, _filters_names):
        self.__filters_names__ = _filters_names
        if _filters_names is not None:
            map(self.addFilter, get_as_list(_filters_names))
        else:
            self.__filters__ = []

    def addFilter(self, name_or_object):
        """
        [optional]
        add a filter function
        the filter function have to have the following signature:
            <name>(data_vector, excluded_annotations)
        -----------------------------------------------------------------------
        commentary:
        data_vector - parameter of type pymath.model.data_vector.DataVector
          DataVector has the following members (fields):
           signal (numpy array) - the whole data signal (or part of the signal)
           annotation (numpy array) - annotation data correspond to signal data
           signal_plus (numpy array) - part of the signal data which
                                       corresponds to RRi(n)
           signal_minus (numpy array) - part of the signal data which
                                       corresponds to RRi(n+1)
           signal_unit - unit of signal column
                                       (defaults to millisecond - ms)
           time - (numpy array) time data column (for future use)

        a custom filter function have to return an object of type DataVector
        """
        self.__filters__.append(name_or_object)

    @property
    def filters(self):
        return self.__filters__

    def setProperties(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'filters', self.filters)
