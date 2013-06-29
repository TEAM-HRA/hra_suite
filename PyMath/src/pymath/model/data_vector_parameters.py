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
        self.__sample_step__ = None
        self.__stepper__ = None
        self.__stepper_size__ = None
        self.__stepper_unit__ = None

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
        setattr(_object, 'sample_step', self.sample_step)
        setattr(_object, 'stepper', self.stepper)
        setattr(_object, 'stepper_size', self.stepper_size)
        setattr(_object, 'stepper_unit', self.stepper_unit)

    def validateDataVectorParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL): # @IgnorePep8
        if self.window_size is None or self.window_size == 0:
            return 'window size has to be set'
        if check_level >= CoreParameters.NORMAL_CHECK_LEVEL:
            if self.signal_index is None:
                return 'signal index has to be set'

    @property
    def sample_step(self):
        """
        [optional, positive integer]
        how big have to be a step for window resampling size;
        it is assumed that this quantity is expressed in signal unit"""
        return self.__sample_step__

    @sample_step.setter
    def sample_step(self, _sample_step):
        self.__sample_step__ = _sample_step

    @property
    def stepper(self):
        """
        [optional]
        stepper size is an amount by which processing window will be jump
        during processing of data, this value could be expressed in
        number of data items or in time units by suffix:
        s - second, m - minute, h - hour; examples: 100, 5m
        """
        return self.__stepper__

    @stepper.setter
    def stepper(self, _stepper):
        if not _stepper == None:
            self.__stepper__ = _stepper
            self.__stepper_size__ = extract_number(_stepper, convert=int)
            self.__stepper_unit__ = extract_alphabetic(_stepper,
                                                       convert=str.lower)

    @property
    def stepper_unit(self):
        """
        [optional]
        stepper unit, as a separate property,
        acceptable values: s - second, m - minute, h - hour
        """
        return self.__stepper_unit__

    @stepper_unit.setter
    def stepper_unit(self, _stepper_unit):
        self.__stepper_unit__ = _stepper_unit

    @property
    def stepper_size(self):
        """
        [optional]
        stepper size, as a separate property
        """
        return self.__stepper_size__

    @stepper_size.setter
    def stepper_size(self, _stepper_size):
        self.__stepper_size__ = _stepper_size

    def parameters_infoDataVectorParameters(self):
        if not self.window_shift == 1:
            print('Window shift: ' + str(self.window_shift))

        if self.__excluded_annotations__ == ALL_ANNOTATIONS:
            print('Excluded annotations: ALL')
        elif not self.__excluded_annotations__ == None:
            print('Excluded annotations: ' + str(self.__excluded_annotations__)) # @IgnorePep8

        if not self.ordinal_column_name == None:
            print('Ordinal column name: ' + str(self.ordinal_column_name))

        if not self.window_size == None:
            print('Window size: ' + str(self.window_size))

        if not self.window_size_unit == None:
            print('Window size unit: ' + str(self.window_size_unit))

        if not self.signal_index == None and self.signal_index >= 0:
            print('Signal index: ' + str(self.signal_index))

        if not self.annotation_index == None and self.annotation_index >= 0:
            print('Annotation index: ' + str(self.annotation_index))

        if not self.time_index == None and self.time_index >= 0:
            print('Time index: ' + str(self.time_index))

        if not self.sample_step == None:
            print('Sample step: ' + str(self.sample_step))

        if not self.stepper == None:
            print('Stepper: ' + str(self.stepper))
