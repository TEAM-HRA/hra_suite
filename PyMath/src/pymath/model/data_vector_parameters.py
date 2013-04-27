'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from pycore.misc import extract_number
    from pycore.misc import extract_alphabetic
    from pycore.collections_utils import nvl
    from pycore.collections_utils import get_as_list
    from pymath.model.utils import ALL_ANNOTATIONS
    from pymath.model.core_parameters import CoreParameters
except ImportError as error:
    print_import_error(__name__, error)


class DataVectorParameters(CoreParameters):
    """
    parameter concerning data vector
    """

    NAME = "data_vector_parameters"

    def __init__(self):
        self.__window_shift__ = 1
        self.__excluded_annotations__ = ALL_ANNOTATIONS

    @property
    def window_size(self):
        """
        [obligatory]
        data window size expressed in number of data items or
        in time units by suffix: s - second, m - minute, h - hour;
        examples: 100, 5m
        """
        return self.__window_size__

    @window_size.setter
    def window_size(self, _window_size):
        self.__window_size__ = extract_number(_window_size, convert=int)
        self.__window_size_unit__ = extract_alphabetic(_window_size,
                                                       convert=str.lower)

    @property
    def window_size_unit(self):
        """
        [optional]
        window size unit, as a separate property,
        acceptable values: s - second, m - minute, h - hour
        """
        return self.__window_size_unit__

    @window_size_unit.setter
    def window_size_unit(self, _window_size_unit):
        self.__window_size_unit__ = _window_size_unit

    @property
    def signal_index(self):
        """
        [obligatory]
        an index of a signal column (0 - based)
        """
        return self.__signal_index__

    @signal_index.setter
    def signal_index(self, _signal_index):
        self.__signal_index__ = _signal_index

    @property
    def annotation_index(self):
        """
        [optional if annotations are not present in input files]
        an index of an annotation column (0 - based)
        """
        return self.__annotation_index__

    @annotation_index.setter
    def annotation_index(self, _annotation_index):
        self.__annotation_index__ = _annotation_index

    @property
    def time_index(self):
        """
        [optional]
        an index of a time column (0 - based) [for future use]
        """
        return self.__time_index__

    @time_index.setter
    def time_index(self, _time_index):
        self.__time_index__ = _time_index

    @property
    def window_shift(self):
        """
        [optional]
        a data window shift between two sets of signals which constitute
        a poincare plot, default value 1
        """
        return nvl(self.__window_shift__, 1)

    @window_shift.setter
    def window_shift(self, _window_shift):
        self.__window_shift__ = _window_shift

    @property
    def excluded_annotations(self):
        """
        [optional]
        specifies, as a string separated by comma or as a list,
        which values (separated by a comma) have to be interpreted
        as true annotations values; if not specified then all non-0 values are
        annotation values
        """
        return self.__excluded_annotations__

    @excluded_annotations.setter
    def excluded_annotations(self, _excluded_annotations):
        if isinstance(_excluded_annotations, str):
            self.__excluded_annotations__ = get_as_list(_excluded_annotations)
        else:
            self.__excluded_annotations__ = _excluded_annotations

    @property
    def ordinal_column_name(self):
        """
        [optional]
        name of the ordinal column (values of an ordinal column is index
        or time what depends on window size unit);
        this column will be the first column in outcome data files
        """
        return self.__ordinal_column_name__

    @ordinal_column_name.setter
    def ordinal_column_name(self, _ordinal_column_name):
        self.__ordinal_column_name__ = _ordinal_column_name

    def setObjectDataVectorParameters(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'window_shift', self.window_shift)
        setattr(_object, 'excluded_annotations', self.excluded_annotations)
        setattr(_object, 'ordinal_column_name', self.ordinal_column_name)
        setattr(_object, 'window_size', self.window_size)
        setattr(_object, 'window_size_unit', self.window_size_unit)
        setattr(_object, 'signal_index', self.signal_index)
        setattr(_object, 'annotation_index', self.annotation_index)
        setattr(_object, 'time_index', self.time_index)

    def validateDataVectorParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL): # @IgnorePep8
        if self.window_size is None or self.window_size == 0:
            return 'window size has to be set'
        if check_level >= CoreParameters.NORMAL_CHECK_LEVEL:
            if self.signal_index is None:
                return 'signal index has to be set'
