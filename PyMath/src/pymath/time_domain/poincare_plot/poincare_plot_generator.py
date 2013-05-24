'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import os
    from pycore.collections_utils import nvl
    from pycore.misc import Params
    from pycore.misc import format_decimal
    from pycore.utils import ProgressMark
    from pycore.utils import ControlInterruptHandler
    from pymath.utils.io_utils import NumpyCSVFile
    from pymath.model.core_parameters import CoreParameters
    from pymath.model.data_vector_segmenter import DataVectorSegmenter
    from pymath.model.data_vector_parameters import DataVectorParameters
    from pymath.model.file_data_parameters import FileDataParameters
    from pymath.statistics.statistic_parameters import StatisticParameters
    from pymath.time_domain.poincare_plot.poincare_plot_parameters import PoincarePlotParameters # @IgnorePep8
    from pymath.time_domain.poincare_plot.filters.filter_parameters import FilterParameters # @IgnorePep8
    from pymath.frequency_domain.fourier_parameters import FourierParameters
    from pymath.statistics.statistics import StatisticsFactory
    from pymath.statistics.summary_statistics import SummaryStatisticsFactory
    from pymath.statistics.summary_statistics import get_summary_statistics_for_csv # @IgnorePep8
    from pymath.statistics.summary_statistics import get_summary_statistics_order_for_csv # @IgnorePep8
    from pymath.statistics.statistic_parameters import extended_statistics_classes # @IgnorePep8
    #from pymath.frequency_domain.fourier import FourierTransformationManager
    from pymath.time_domain.poincare_plot.filters.filter_manager import FilterManager # @IgnorePep8
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotGenerator(object):
    """
    this is an engine to generate poincare plot statistics
    """
    def __init__(self, **params):
        self.__prepare_parameters__(**params)
        self.__error_message__ = None
        self.__info_message__ = None

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    def checkParameters(self, check_level=None):

        if check_level == None:
            check_level = CoreParameters.NORMAL_CHECK_LEVEL
        for class_name, parameter_name in self.__parameters_ids__:
            param_object = getattr(self.params, parameter_name, None)
            if param_object:
                validate_method = getattr(param_object,
                                    'validate' + class_name, None)
                if validate_method:
                    message = validate_method(check_level)
                    if message:
                        return message

    def precheck(self, reference_filename):
        message = None
        if self.skip_existing_outcomes and reference_filename:
            #check if output file for normal statistics exists already
            with NumpyCSVFile(output_dir=self.output_dir,
                           reference_filename=reference_filename) as csv:
                if not os.path.exists(csv.output_file):
                    #check if output file for summary statistics exists already
                    with NumpyCSVFile(output_dir=self.output_dir,
                                       reference_filename=reference_filename,
                                       output_suffix='_sum') as csv:
                        pass
            if os.path.exists(csv.output_file):
                message = 'Skipping processing, the outcome file ' + str(csv.output_file) + ' exists !' # @IgnorePep8
                self.params.info_handler(message)
        return (True, None,) if message == None else (False, message,)

    def generate(self, data_vector, start_progress=None,
                 progress_handler=None):
        """
        generate poincare plots
        """
        if not start_progress == None:
            if hasattr(start_progress, 'progress_mark'):
                if start_progress.progress_mark == None:
                    start_progress.progress_mark = self.progress_mark
            if hasattr(start_progress, 'info_handler'):
                if start_progress.info_handler == None:
                    start_progress.info_handler = self.params.info_handler
        return self.__generate_core__(data_vector,
                                       start_progress=start_progress,
                                       progress_handler=progress_handler)

    def generate_CSV(self, data_vector, reference_filename,
                                  start_progress=None, progress_handler=None):
        """
        generates poincare plots and saves outcomes to csv files
        """
        with NumpyCSVFile(output_dir=self.output_dir,
                        reference_filename=reference_filename,
                        output_precision=self.output_precision,
                        print_output_file=True,
                        ordinal_column_name=self.ordinal_column_name,
                        output_separator=self.output_separator,
                        sort_headers=False,
                        add_headers=self.add_headers,
                        ordered_headers=self.statistics_names) as csv:

            if not start_progress == None:
                start_progress.reference_filename = reference_filename
                if hasattr(start_progress, 'progress_mark'):
                    if start_progress.progress_mark == None:
                        start_progress.progress_mark = self.progress_mark
                if hasattr(start_progress, 'info_handler'):
                    if start_progress.info_handler == None:
                        start_progress.info_handler = self.params.info_handler

            if not progress_handler == None:
                progress_handler.csv = csv

            not_interrupted = self.__generate_core__(data_vector,
                                        start_progress=start_progress,
                                        progress_handler=progress_handler)

        if not_interrupted:
            if csv.info_message:
                self.params.info_handler(csv.info_message)
            if csv.error_message:
                self.params.info_handler(csv.error_message)
                return

            #give info about saved file
            if csv.saved and self.params.output_file_listener:
                self.params.output_file_listener(csv.output_file)

            if not self.summary_statistics == None:
                #get ordered headers for summary statistics
                ordered_headers = get_summary_statistics_order_for_csv(
                                            self.summary_statistics_order)
                with NumpyCSVFile(output_dir=self.output_dir,
                     reference_filename=reference_filename,
                     output_precision=self.output_precision,
                     print_output_file=True,
                     output_separator=self.output_separator,
                     sort_headers=False,
                     add_headers=self.add_headers,
                     output_suffix='_sum',
                     ordered_headers=ordered_headers,
                     message='\nSummary statistics saved into the file: ') as summary_csv: # @IgnorePep8
                    summary_csv.write(get_summary_statistics_for_csv(self.summary_statistics)) # @IgnorePep8

                #give info about saved summary file
                if summary_csv.saved and self.params.output_file_listener:
                    self.params.output_file_listener(
                                                summary_csv.output_file)
        return not_interrupted

    def __generate_core__(self, data_vector, start_progress,
                          progress_handler=None):
        """
        core functionality to generate poincare plots
        """

#        fourier = FourierTransformationManager(self.fourier_transformation,
#                                    self.fourier_transform_interpolation)
        filter_manager = FilterManager(_shift=self.window_shift,
                        _excluded_annotations=self.excluded_annotations,
                        _filters=self.filters)

        #there could be the case when only statistics name are defined
        #and then we have to extract from the names corresponding classes
        statistics_classes = extended_statistics_classes(
                self.statistics_classes, self.statistics_names,
                self.summary_statistics_classes, self.summary_statistics_names)

        statisticsFactory = StatisticsFactory(
                        statistics_names=self.statistics_names,
                        statistics_classes=statistics_classes,
                        statistics_handlers=self.statistics_handlers,
                        _use_identity_line=self.use_identity_line,
                        use_buffer=self.use_buffer)
        if not statisticsFactory.has_statistics:
            return True
        summaryStatisticsFactory = SummaryStatisticsFactory(
                summary_statistics_names=self.summary_statistics_names,
                summary_statistics_classes=self.summary_statistics_classes)

        segmenter = DataVectorSegmenter(data_vector,
                            self.window_size,
                            shift=self.window_shift,
                            window_size_unit=self.window_size_unit,
                            normalize_window_size=self.normalize_window_size,
                            filter_manager=filter_manager,
                            window_resampling_step=self.window_resampling_step,
                            jump_step=self.jump_step,
                            jump_step_unit=self.jump_step_unit)

        start_progress.segmenter = segmenter
        start_progress()
        progress = start_progress.progress
        if progress == False:
            return False

        interrupter = ControlInterruptHandler()
        parameters = {}
        parameters_old = None
        data_segment_old = None
        for data_segment in segmenter:
            if interrupter.isInterrupted():
                break
            if segmenter.data_changed:
                parameters.clear()
                parameters_old = None
                data_segment_old = None
            else:
                parameters = parameters_old
                data_segment = data_segment_old

            if progress:
                tick = getattr(progress, 'tick')
                if tick:
                    tick()

            if segmenter.data_changed:
                data_segment = filter_manager.run_filters(data_segment)

            #this could happened when for example annotation
            #filter is used and all data are annotated that means
            #all signal data are filtered out
            if len(data_segment.signal) == 0:
                parameters_old = parameters
                data_segment_old = data_segment
                continue

            #this situation could occur when there is a normal signal after
            #a long series of annotated signals
            if segmenter.data_changed:
                if len(data_segment.signal) == 1:
                    continue

            #fourier_params = fourier.calculate(data_segment,
            #                                   self.excluded_annotations)
            #parameters.update(fourier_params)

            if segmenter.data_changed:
                statistics = statisticsFactory.statistics(data_segment)
                parameters.update(statistics)

            if progress_handler:
                if segmenter.data_changed:
                    progress_handler.parameters = parameters
                    progress_handler.segmenter = segmenter
                    progress_handler()
                if progress_handler.interrupted:
                    #mark interrupt state of interrupter to give consistent
                    #behaviour to the rest of the code
                    interrupter.interrupt()
                    break

            summaryStatisticsFactory.update(parameters, data_segment)
            if segmenter.data_changed:
                parameters_old = parameters
                data_segment_old = data_segment

        self.summary_statistics = None
        if interrupter.isInterrupted() == False:
            if summaryStatisticsFactory.has_summary_statistics > 0:
                self.summary_statistics = summaryStatisticsFactory.summary_statistics # @IgnorePep8
                self.summary_statistics_order = summaryStatisticsFactory.summary_statistics_order # @IgnorePep8

        if progress:
            close = getattr(progress, 'close')
            if close:
                close()
        interrupted = interrupter.isInterrupted()
        interrupter.clean()
        return not interrupted

    def __default_info_handler__(self, info):
        print('\n' + info)

    def __prepare_parameters__(self, **params):
        self.params = Params(**params)

        if self.params.info_handler == None:
            self.params.info_handler = self.__default_info_handler__

        for class_name, parameter_name in self.__parameters_ids__:
            param_object = getattr(self.params, parameter_name, None)
            if param_object:
                set_method = getattr(param_object,
                                    'setObject' + class_name, None)
                if set_method:
                    set_method(self)

    @property
    def summary_statistics(self):
        return self.__summary_statistics__

    @summary_statistics.setter
    def summary_statistics(self, _summary_statistics):
        self.__summary_statistics__ = _summary_statistics

    @property
    def formatted_summary_statistics(self):
        formatted_statistics = {}
        for statistic, value in self.summary_statistics.items():
            formatted_statistics[statistic] = format_decimal(value,
                                                self.output_precision)
        return formatted_statistics

    @property
    def parameters_info(self):
        print('')
        if self.statistics_names:
            print('Using statistics: ' + self.statistics_names)
        if self.statistics_handlers:
            print('Using statistics handlers/functions:')
            for _handler in self.statistics_handlers:
                print('   name: ' + _handler.name)
        if self.summary_statistics_names:
            print('Using summary statistics: ' + self.summary_statistics_names)
        print('Using output precision: ' + str(self.output_precision))
        print('Using buffer: ' + str(self.use_buffer))
        if not self.filters_names == None:
            print('Using filters: ' + str(self.filters_names))
        print('Window size: ' + str(self.window_size) +
              nvl(self.window_size_unit, ''))
        print('Using buffer: ' + str(self.use_buffer))
        print('Skip for existing outcomes: '
              + str(self.skip_existing_outcomes))

    @property
    def __parameters_ids__(self):
        """
        method returns class names and name identifiers of all parameter
        classes used in poincare plot generator
        """
        return [(DataVectorParameters.__name__, DataVectorParameters.NAME),
                (FileDataParameters.__name__, FileDataParameters.NAME),
                (StatisticParameters.__name__, StatisticParameters.NAME),
                (PoincarePlotParameters.__name__, PoincarePlotParameters.NAME),
                (FilterParameters.__name__, FilterParameters.NAME),
                (FourierParameters.__name__, FourierParameters.NAME)]

    def segment_count(self, data_vector):
        """
        calculates approximate number of segments count during
        processing of poincare plot
        """
        filter_manager = FilterManager(_shift=self.window_shift,
                        _excluded_annotations=self.excluded_annotations,
                        _filters=self.filters)
        segmenter = DataVectorSegmenter(data_vector,
                            self.window_size,
                            shift=self.window_shift,
                            window_size_unit=self.window_size_unit,
                            normalize_window_size=self.normalize_window_size,
                            filter_manager=filter_manager,
                            window_resampling_step=self.window_resampling_step,
                            jump_step=self.jump_step,
                            jump_step_unit=self.jump_step_unit)
        return segmenter.segment_count()


class StartProgressGenerator(object):
    """
    callable class used when process of poincare plots generation is
    started
    """
    def __init__(self):
        self.__progress__ = None

    def check(self):
        segment_count = self.segmenter.segment_count()
        if segment_count == -1:
            self.params.info_handler("Window size can't be greater then data size !!!") # @IgnorePep8
            self.__progress__ = False
            return False
        return True

    def __call__(self):
        if self.check():
            if self.progress_mark:
                self.__progress__ = ProgressMark(_label='Processing data...', # @IgnorePep8
                                _max_count=self.segmenter.segment_count())
            else:
                self.params.info_handler('Processing data')

    @property
    def progress(self):
        return self.__progress__


class ProgressHandlerGenerator(object):
    """
    the base class for progress handler in poincare plot processing loop
    """

    @property
    def interrupted(self):
        """
        returns true if process is interrupted
        """
        return False


class CSVStartProgressGenerator(StartProgressGenerator):
    """
    callable class used when process of poincare plots generation is
    started and csv files have to be created
    """
    def __call__(self):
        if self.check():
            if self.progress_mark:
                self.__progress__ = ProgressMark(
                                _label='Processing file ' +
                                self.reference_filename + ' ...',
                                _max_count=self.segmenter.segment_count())
            else:
                self.info_handler('Processing file: ' + self.reference_filename) # @IgnorePep8


class CSVProgressHandlerGenerator(ProgressHandlerGenerator):
    """
    callable class used during creation of csv files of
    poincare plot processing
    """
    def __call__(self):
        self.csv.write(self.parameters,
                       ordinal_value=self.segmenter.ordinal_value)
