'''
Created on 24 kwi 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    from hra_core.collections_utils import get_as_list
    from hra_core.collections_utils import commas
    from hra_math.model.parameters.core_parameters import CoreParameters
except ImportError as error:
    print_import_error(__name__, error)


class FilterParameters(CoreParameters):

    NAME = 'filter_parameters'

    """
    parameters concerning filters
    """
    def __init__(self):
        self.__filters__ = []

    def setAvailableFiltersInfoHandler(self, available_filters_info_handler):
        self.__available_filters_info_handler__ = \
                                            available_filters_info_handler

    def available_filters(self):
        """
        [optional]
        print all available filters names
        """
        if not self.__available_filters_info_handler__ == None:
            print(self.__available_filters_info_handler__())

    @property
    def filters_names(self):
        """
        [optional]
        use filters names (separated by comma)
        to get list of standard filters names call a function:
        get_filters_short_names()
        [module: hra_math.time_domain.poincare_plot.poincare_plot]
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
        data_vector - parameter of type hra_math.model.data_vector.DataVector
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

    @filters.setter
    def filters(self, _filters):
        self.__filters__ = _filters

    def setObjectFilterParameters(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'filters', self.filters)
        setattr(_object, 'filters_names', self.filters_names)

    def clearFilters(self):
        self.__filters__ = []

    def validateFilterParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL): # @IgnorePep8
        pass

    def parameters_infoFilterParameters(self):
        if not self.__filters_names__ == None \
            and len(self.__filters_names__) > 0:
            print('Filters: ' + commas(self.__filters_names__))
