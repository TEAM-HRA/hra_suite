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
    from pymath.model.data_vector_segmenter import DataVectorSegmenter
    from pymath.utils.io_utils import NumpyCSVFile
    from pymath.statistics.statistics import StatisticsFactory
    from pymath.statistics.summary_statistics import SummaryStatisticsFactory
    from pymath.frequency_domain.fourier import FourierTransformationManager
    from pymath.time_domain.poincare_plot.filters.filter_manager import FilterManager # @IgnorePep8
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotGenerator():
    """
    this is an engine to generate poincare plot statistics
    """
    def __init__(self, **params):
        self.__prepare_parameters__(**params)
        self.__error_message__ = None
        self.__info_message__ = None

    def checkParameters(self):
        message = None
        if self.statistics_names == None or len(self.statistics_names) == 0:
            message = 'no statistics names has been chosen'
        elif self.data_file is None and self.data_dir is None:
            message = 'data_file or data_dir have to be set'
        elif self.output_dir is None:
            message = 'output_dir has to be set'
        elif self.window_size is None:
            message = 'window size has to be set'
        elif self.signal_index is None:
            message = 'signal index has to be set'
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
                message = 'Skipping processing, the outcome file ' + \
                              + str(csv.output_file) + ' exists !'
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
                         output_headers=self.output_headers,
                         ordered_headers=self.statistics_names) as csv:

            fourier = FourierTransformationManager(self.fourier_transformation,
                                        self.fourier_transform_interpolation)
            filter_manager = FilterManager(_shift=self.window_shift,
                            _excluded_annotations=self.excluded_annotations,
                            _filters=self.filters)

            statisticsFactory = StatisticsFactory(self.statistics_names,
                            statistics_handlers=self.statistics_handlers,
                            _use_identity_line=self.use_identity_line,
                            use_buffer=self.use_buffer)
            if not statisticsFactory.has_statistics:
                return True
            summaryStatisticsFactory = SummaryStatisticsFactory(
                                                self.summary_statistics_names)

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

                data_segment = filter_manager.filter(data_segment)

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
                self.__summary_statistics__ = summaryStatisticsFactory.summary_statistics # @IgnorePep8
                if reference_filename:
                    summary_headers = summaryStatisticsFactory.summary_statistics.keys() # @IgnorePep8
                    #save summary statistics into a file
                    with NumpyCSVFile(output_dir=self.output_dir,
                         reference_filename=reference_filename,
                         output_precision=self.output_precision,
                         print_output_file=True,
                         output_separator=self.output_separator,
                         sort_headers=False,
                         output_headers=summary_headers,
                         output_suffix='_sum',
                         message='\nSummary statistics saved into the file: ') as summary_csv: # @IgnorePep8

                        summary_csv.write(self.__summary_statistics__)

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

        if self.params.file_data_parameters:
            self.params.file_data_parameters.setFileDataProperties(self)

        if self.params.fourier_parameters:
            self.params.fourier_parameters.setFourierProperties(self)

        if self.params.data_vector_parameters:
            self.params.data_vector_parameters.setDataVectorProperties(self)

        if self.params.filter_parameters:
            self.params.filter_parameters.setFilterProperties(self)

        if self.params.statistic_parameters:
            self.params.statistic_parameters.setStatisticProperties(self)

        if self.params.poincare_plot_parameters:
            self.params.poincare_plot_parameters.setPoincarePlotProperties(self) # @IgnorePep8

    def summary_statistics(self):
        return self.__summary_statistics__

    @property
    def parameters_info(self):
        print('Using statistics: ' + self.statistics_names)
        if self.statistics_handlers:
            print('Using statistics handlers/functions:')
            for _handler in self.statistics_handlers:
                print('   name: ' + _handler.name)
        if self.summary_statistics_names:
            print('Using summary statistics: ' + self.summary_statistics_names)
        print('Using output precision: ' + self.output_precision)
        print('Using buffer: ' + str(self.use_buffer))
        if not self.filters_names == None:
            print('Using filters: ' + str(self.filters_names))
        print('Window size: ' + str(self.window_size) +
              nvl(self.window_size_unit, ''))
        print('Using buffer: ' + str(self.use_buffer))
        print('Skip for existing outcomes: '
              + str(self.skip_existing_outcomes))
