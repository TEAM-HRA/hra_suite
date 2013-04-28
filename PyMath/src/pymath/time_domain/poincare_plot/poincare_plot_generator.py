'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import os
    from pycore.collections_utils import nvl
    from pycore.misc import Params
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
    from pymath.frequency_domain.fourier import FourierTransformationManager
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

    def checkParameters(self, check_level=CoreParameters.NORMAL_CHECK_LEVEL):

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

    def generate(self, data_vector, reference_filename=None):
        parameters = {}
        self.__summary_statistics__ = None
        with NumpyCSVFile(output_dir=self.output_dir,
                         reference_filename=reference_filename,
                         output_precision=self.output_precision,
                         print_output_file=True,
                         ordinal_column_name=self.ordinal_column_name,
                         output_separator=self.output_separator,
                         sort_headers=False,
                         add_headers=self.add_headers,
                         ordered_headers=self.statistics_names) as csv:

            fourier = FourierTransformationManager(self.fourier_transformation,
                                        self.fourier_transform_interpolation)
            filter_manager = FilterManager(_shift=self.window_shift,
                            _excluded_annotations=self.excluded_annotations,
                            _filters=self.filters)

            statisticsFactory = StatisticsFactory(
                            statistics_names=self.statistics_names,
                            statistics_classes=self.statistics_classes,
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
                                    window_size_unit=self.window_size_unit)
            progress = None
            segment_count = segmenter.segment_count()

            if self.progress_mark:
                if reference_filename:
                    progress = ProgressMark(_label='Processing file ' +
                                        reference_filename + ' ...',
                                        _max_count=segment_count)
                else:
                    progress = ProgressMark(_label='Processing data...',
                                                 _max_count=segment_count)
            else:
                if reference_filename:
                    self.params.info_handler('Processing file: ' + reference_filename) # @IgnorePep8
                else:
                    self.params.info_handler('Processing data')
            if segment_count == -1:
                csv.error_message = "Window size can't be greater then data size !!!" # @IgnorePep8
                self.params.info_handler(csv.error_message)
                return False

            interrupter = ControlInterruptHandler()
            for data_segment in segmenter:
                if interrupter.isInterrupted():
                    break
                if progress:
                    progress.tick

                data_segment = filter_manager.run_filters(data_segment)

                #this could happened when for example annotation
                #filter is used and all data are annotated that means
                #all signal data are filtered out
                if len(data_segment.signal) == 0:
                    continue

                fourier_params = fourier.calculate(data_segment,
                                                   self.excluded_annotations)
                parameters.update(fourier_params)

                statistics = statisticsFactory.statistics(data_segment)
                parameters.update(statistics)

                csv.write(parameters, ordinal_value=segmenter.ordinal_value)

                summaryStatisticsFactory.update(statistics, data_segment)
                #print(str(statistics))

                parameters.clear()

        if interrupter.isInterrupted() == False:
            if csv.info_message:
                self.params.info_handler(csv.info_message)
            if csv.error_message:
                self.params.info_handler(csv.error_message)
                return

            if summaryStatisticsFactory.has_summary_statistics > 0:
                self.summary_statistics = summaryStatisticsFactory.summary_statistics # @IgnorePep8
                if reference_filename:
                    #save summary statistics into a file
                    with NumpyCSVFile(output_dir=self.output_dir,
                         reference_filename=reference_filename,
                         output_precision=self.output_precision,
                         print_output_file=True,
                         output_separator=self.output_separator,
                         sort_headers=False,
                         add_headers=self.add_headers,
                         output_suffix='_sum',
                         message='\nSummary statistics saved into the file: ') as summary_csv: # @IgnorePep8

                        summary_csv.write(summaryStatisticsFactory.summary_statistics_for_csv) # @IgnorePep8

        if progress:
            progress.close
        interrupted = interrupter.isInterrupted()
        interrupter.clean()
        return not interrupted

    def __info_handler__(self, info):
        print('\n' + info)

    def __prepare_parameters__(self, **params):
        self.params = Params(**params)

        if self.params.info_handler == None:
            self.params.info_handler = self.__info_handler__

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
    def parameters_info(self):
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
