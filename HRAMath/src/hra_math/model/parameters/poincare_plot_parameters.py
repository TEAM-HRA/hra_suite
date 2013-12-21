'''
Created on 24 kwi 2013

@author: jurek
'''

from hra_math.utils.utils import print_import_error
try:
    import multiprocessing
    from hra_core.io_utils import DataFileHeader
    from hra_core.misc import extract_number
    from hra_core.misc import is_positive
    from hra_core.misc import ColorRGB
    from hra_core.misc import is_empty
    from hra_core.misc import Separator
    from hra_core.misc import extract_alphabetic
    from hra_core.collections_utils import get_as_list
    from hra_core.collections_utils import get_as_tuple
    from hra_core.collections_utils import commas
    from hra_core.collections_utils import get_index_of_string
    from hra_core.collections_utils import nvl
    from hra_math.model.parameters.core_parameters import CoreParameters
    from hra_math.model.utils import ALL_ANNOTATIONS
    from hra_math.time_domain.poincare_plot.filters.filter_utils \
        import get_filters_short_names
    from hra_math.statistics.statistics_utils import available_statistics_info
except ImportError as error:
    print_import_error(__name__, error)

DEFAULT_OUTPUT_PRECISION = (10, 5)


class PoincarePlotParameters(CoreParameters):
    """
    poincare plot parameters
    """

    NAME = "poincare_plot_parameters"

    def __init__(self):
        self.__available_filters_info_handler__ = get_filters_short_names
        self.__available_statistics_info_handler__ = available_statistics_info
        self.__all_annotations_ident__ = ALL_ANNOTATIONS
        self.use_identity_line = True
        self.use_buffer = True
        self.window_shift = 1
        self.extension = '*'
        self.output_separator = Separator.WHITE_SPACE.sign  # @UndefinedVariable # @IgnorePep8
        self.filters = []

        self.movie_fps = 700
        self.movie_active_color = ColorRGB(255, 0, 0)
        self.movie_inactive_color = ColorRGB(0, 0, 0)
        self.movie_centroid_color = ColorRGB(0, 255, 0)
        self.movie_active_size = 3
        self.movie_inactive_size = 3
        self.movie_centroid_size = 4
        self.movie_dpi = 70
        self.movie_height = 550
        self.movie_width = 550
        self.movie_skip_frames = True
        self.movie_save_partial = True
        self.movie_skip_to_frame = 0
        self.movie_not_save = False
        self.movie_show_plot_legends = False
        self.movie_bin_size = 500
        self.movie_experimental_code = False
        self.movie_animated = False
        self.movie_calculate_all_frames = True
        self.movie_standard_generation = False
        self.movie_prefixed_by_source = True
        self.movie_clean_frames = True

        self.statistics_handlers = []
        self.statistics_classes = []

        self.summary_statistics_classes = []
        self.__parameters_info__ = {}

    def setAllAnnotationsIdent(self, _all_annotations_ident):
        self.__all_annotations_ident__ = _all_annotations_ident
        if self.excluded_annotations == None:
            self.excluded_annotations = self.__all_annotations_ident__

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
        self.filters.append(name_or_object)

    def clearFilters(self):
        self.filters = []

    def setAvailableStatisticsInfoHandler(self,
                                          available_statistics_info_handler):
        self.__available_statistics_info_handler__ \
                                        = available_statistics_info_handler

    def available_statistics(self):
        """
        [optional]
        print all available statistics names
        """

        if self.__available_statistics_info_handler__ == None:
            for _info in self.__available_statistics_info_handler__():
                print(_info)

    def addStatisticHandler(self, _handler, _name):
        """
        [optional]
        add a statistic function (or handler) with optional _name
        all parameters of this function are type of numpy.array;
        parameter _name is a name of a column in an outcome file associated
        with this statistic function,
        the function could have the following signatures:
            <function name>(signal)
            <function name>(signal, annotation)
            <function name>(signal, signal_plus, signal_minus)
            <function name>(signal, signal_plus, signal_minus, annotation)
        -----------------------------------------------------------------------
        commentary:
        signal - the whole data signal (or part of it)
        annotation - annotation data correspond to signal data
        signal_plus - part of the signal data which corresponds to RRi(n)
        signal_minus - part of the signal data which corresponds to RRi(n+1)
        """
        if self.statistics_handlers == None:
            self.statistics_handlers = []
        _handler.name = _name
        self.statistics_handlers.append(_handler)

    def removeStatisticHandler(self, _name):
        """
        [optional]
        remove statistic handler/function associated with a _name
        """
        for idx, _handler in enumerate(self.statistics_handlers):
            if _handler.name == _name:
                del self.statistics_handlers[idx]
                return

    def clearSummaryStatisticsClasses(self):
        self.summary_statistics_classes = []

    @property
    def summary_statistics_is_selected(self):
        """
        method returns true if there is any summary statistics selected
        """
        return not (is_empty(self.summary_statistics_names) and \
                is_empty(self.summary_statistics_classes))

    @summary_statistics_is_selected.setter
    def summary_statistics_is_selected(self, _dummy):
        pass

    def clearStatisticsClasses(self):
        self.statistics_classes = []

    def validateParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL): # @IgnorePep8
        if self.output_precision == None:
            return "Output precision is required"
        if check_level >= CoreParameters.MEDIUM_CHECK_LEVEL:
            if self.output_separator == None:
                return "Output separator is required"
            if self.output_dir == None:
                return "Output directory is required"
#        if is_empty(self.statistics_names) and \
#            is_empty(self.statistics_classes) and \
#            is_empty(self.statistics_handlers) and \
#            is_empty(self.summary_statistics_names) and \
#            is_empty(self.summary_statistics_classes):
#            return "Statistics names or classes or handlers are required"

    def prepareParameters(self):
        """
        method prepares poincare plot parameters
        """
        if self.stepper:
            self.stepper_size = extract_number(self.stepper, convert=int)
            self.stepper_unit = extract_alphabetic(self.stepper,
                                                       convert=str.lower)
        self.movie_dir = nvl(self.movie_dir, self.output_dir, '')

        if isinstance(self.excluded_annotations, str):
            self.excluded_annotations = get_as_list(self.excluded_annotations)

        if self.filters_names is not None:
            map(self.addFilter, get_as_list(self.filters_names))
        else:
            self.filters = []

        if self.output_dir:
            # remove leading and trailing whitespaces
            self.output_dir = self.output_dir.strip()

        if self.window_size:
            self.window_size_unit = extract_alphabetic(self.window_size,
                                                       convert=str.lower)
            self.window_size_value = extract_number(self.window_size,
                                                    convert=int)

        self.movie_multiprocessing_factor = nvl(
                                self.movie_multiprocessing_factor,
                                3 if multiprocessing.cpu_count() > 1 else 0)

        if not self.data_file == None:
            self.group_data_filename = None

        if isinstance(self.output_precision, str):
            self.output_precision = get_as_tuple(self.output_precision,
                                                     convert=int)
        elif self.output_precision == None:
            self.output_precision = DEFAULT_OUTPUT_PRECISION

    def parameters_info(self):
        if not self.data_dir == None:
            print('Data file: ' + str(self.data_file))
        elif not self.data_file == None:
            print('Data dir: ' + str(self.data_dir))

        if not self.extension == None:
            print('Extension: ' + str(self.extension))

        if not self.override_existing_outcomes == None:
            print('Override existing outcomes: ' + str(self.override_existing_outcomes)) # @IgnorePep8

        if not self.output_dir == None:
            print('Output dir: ' + str(self.output_dir))

        if not self.output_precision == None:
            print('Output precision: ' + str(self.output_precision))

        if not self.output_separator == None:
            print('Output separator: ' + str(self.output_separator))

        if not self.output_prefix == None:
            print('Output file name prefix: ' + str(self.output_prefix))

        if self.group_data_filename:
            print('Group data filename: ' + str(self.group_data_filename))

        if not self.window_shift == 1:
            print('Window shift: ' + str(self.window_shift))

        if self.excluded_annotations == self.__all_annotations_ident__:
            print('Excluded annotations: ALL')
        elif not self.excluded_annotations == None:
            print('Excluded annotations: ' + str(self.excluded_annotations))

        if not self.ordinal_column_name == None:
            print('Ordinal column name: ' + str(self.ordinal_column_name))

        if self.window_size == None:
            print('Window size: unspecified, assumed the whole recording')
        else:
            print('Window size: ' + str(self.window_size))

        if not self.separator == None:
            print('Data separator: ' + str(self.separator))

        #if not self.window_size_unit == None:
        #    print('Window size unit: ' + str(self.window_size_unit))

        if is_positive(self.signal_index):
            print('Signal index: ' + str(self.signal_index))

        if is_positive(self.annotation_index):
            print('Annotation index: ' + str(self.annotation_index))

        if is_positive(self.time_index):
            print('Time index: ' + str(self.time_index))

        if self.signal_label:
            print('Signal label: ' + self.signal_label)

        if self.annotation_label:
            print('Annotation label: ' + self.annotation_label)

        if self.time_label:
            print('Time label: ' + self.time_label)

        if not self.sample_step == None:
            print('Sample step: ' + str(self.sample_step))

        if not self.stepper == None:
            print('Stepper: ' + str(self.stepper))

        if self.headers_count > 0:
            print('Headers count: ' + str(self.headers_count))

        if not self.time_format == None:
            print('Time format column: ' + str(self.time_format))

        if not self.use_buffer == None:
            print('Use buffer: ' + str(self.use_buffer))

        if not self.use_identity_line == None:
            print('Use line of identity: ' + str(self.use_identity_line))

        if not self.x_label == None:
            print('X label axis: ' + self.x_label)

        if not self.y_label == None:
            print('Y label axis: ' + self.y_label)

        if self.print_first_signal == True:
            print('print_first_signal: ' + str(self.print_first_signal))

        if not self.__filters_names__ == None \
            and len(self.__filters_names__) > 0:
            print('Filters: ' + commas(self.__filters_names__))

        if not self.movie_name == None:
            print('Movie specification: ')
            print('    name: ' + str(self.movie_name))
            print('    directory: ' + str(self.movie_dir))
            print('    height: ' + str(self.movie_height))
            print('    width: ' + str(self.movie_width))
            print('    FPS: ' + str(self.movie_fps))
            print('    active plot color: ' + str(self.movie_active_color))
            print('    inactive plot color: ' +
                                        str(self.movie_inactive_color))
            print('    centroid color: ' + str(self.movie_centroid_color))
            print("    active plot point's size: " +
                                                str(self.movie_active_size))
            print("    inactive plot point's size: " +
                                            str(self.movie_inactive_size))
            print("    centroid point's size: " +
                                            str(self.movie_centroid_size))
            print('    DPI: ' + str(self.movie_dpi))
            print('    skip existing frames: ' + str(self.movie_skip_frames))
            print('    save partial movie: ' + str(self.movie_save_partial))
            print('    skip to frame: ' + str(self.movie_skip_to_frame))
            print('    show plot legends: ' +
                                        str(self.movie_show_plot_legends))
            print('    movie multiprocessing factor: ' +
                                        str(self.movie_multiprocessing_factor))
            print('    movie bin size: ' + str(self.movie_bin_size))
            print('    use animation API: ' + str(self.movie_animated))
            print('    use experimental code: '
                                         + str(self.movie_experimental_code))
            print('    calculate all frames: '
                                        + str(self.movie_calculate_all_frames))
            print('    standard generation: '
                                        + str(self.movie_standard_generation))
            print('    prefix by source: '
                                        + str(self.movie_prefixed_by_source))
            print('    clean frames: ' + str(self.movie_clean_frames))

        if is_empty(self.statistics_names) and \
            is_empty(self.statistics_classes) and \
            is_empty(self.statistics_handlers) and \
            is_empty(self.summary_statistics_names) and \
            is_empty(self.summary_statistics_classes):
            print('Statistics: no statistics selected')
        else:
            if not is_empty(self.statistics_names):
                print('Statistics: ' + commas(self.statistics_names))
            if not is_empty(self.summary_statistics_names):
                print('Summary statistics: ' +
                      commas(self.summary_statistics_names))

    def check_data_indexes(self, _filename, disp):
        #method used by client code explicitly, because of dynamic nature
        #of placement of data columns which have to check at runtime
        #to manage a situation when columns are specified by names and
        #for different files they are placed in different columns
        message = None
        if not nvl(self.signal_label, self.annotation_label,
                   self.time_label) == None:
            headers_count = nvl(self.headers_count, 1)

            file_headers = DataFileHeader(_filename,
                                        _separator=self.separator,
                                        number_of_lines=headers_count)
            #get header's lines
            headers = file_headers.getHeadersLines(headers_count)
            if self.signal_label:
                self.signal_index = get_index_of_string(
                                        self.signal_label, headers,
                                        _separator=self.separator)
            if self.annotation_label:
                self.annotation_index = get_index_of_string(
                                        self.annotation_label, headers,
                                        _separator=self.separator)
                if self.annotation_index == -1:
                    message = ('There is no annotation index for label %s !'
                                                     % (self.annotation_label))
            if self.time_label:
                self.time_index = get_index_of_string(
                                        self.time_label, headers,
                                        _separator=self.separator)
                if self.time_index == -1:
                    message = ('There is no time index for label %s !'
                                                         % (self.time_label))
        if self.signal_index == -1:
            if self.time_label:
                message = ('There is no signal index for label %s !'
                                                        % (self.signal_label))
            else:
                message = 'The signal index has to be set !'

        if is_positive(self.time_index) and self.time_format == None:
            message = 'For time column a time format parameter is required !'

        if not is_positive(self.time_index) and not is_empty(self.time_format):
            message = 'Time format requires time index column selection !'

        if message and disp:
            print('File: %s \n %s \n' % (_filename, message))
            return False
        else:
            return True

    def addParameterInfo(self, name, default, _help):
        """
        add information about poincare plot parameter
        """
        self.__parameters_info__[name] = __ParameterInfo__(name, default,
                                                           _help)

    @property
    def parameters_info_count(self):
        """
        get parameters info count
        """
        return len(self.__parameters_info__)

    def info(self):
        """
        poincare plot parameters info descriptions
        """
        title = "Poincare plot parameters:"
        print(title)
        print("=" * len(title))
        for name in sorted(self.__parameters_info__):
            print(self.__parameters_info__[name].format)
        print("=" * len(title))


class __ParameterInfo__(object):
    """
    poincare plot parameter info class
    """
    def __init__(self, name, default, _help):
        self.name = name
        self.default = default
        self._help = _help

    @property
    def format(self):
        return "%s %s %s" % (self.name, self._help, self.default)
