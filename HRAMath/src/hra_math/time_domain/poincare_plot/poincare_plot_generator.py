'''
Created on 24 kwi 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import os
    from hra_core.misc import format_decimal
    from hra_core.utils import ProgressMark
    from hra_core.utils import ControlInterruptHandler
    from hra_math.utils.io_utils import NumpyCSVFile
    from hra_math.model.data_vector_segmenter import SegmenterManager
    from hra_math.time_domain.poincare_plot.poincare_plot_movie_maker \
        import PoincarePlotMovieMaker
    from hra_math.statistics.statistics import StatisticsFactory
    from hra_math.statistics.summary_statistics import SummaryStatisticsFactory
    from hra_math.statistics.summary_statistics \
        import get_summary_statistics_for_csv
    from hra_math.statistics.summary_statistics \
        import get_summary_statistics_order_for_csv
    from hra_math.statistics.statistics_utils \
        import extended_statistics_classes
    from hra_math.time_domain.poincare_plot.filters.filter_manager \
        import FilterManager
except ImportError as error:
    print_import_error(__name__, error)


class PoincarePlotGenerator(object):
    """
    this is an engine to generate poincare plot statistics
    """
    def __init__(self, **params):
        self.__error_message__ = None
        self.__info_message__ = None
        self.__p__ = params.get("parameters")
        self.__info_handler__ = params.get("info_handler",
                                       self.__empty_info_handler__)

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    def __empty_info_handler__(self, message):
        pass

    def precheck(self, reference_filename):
        message = None
        self.__outcome_exists__ = False
        if self.__p__.override_existing_outcomes == False \
            and reference_filename:
            #check if output file for normal statistics exists already
            with NumpyCSVFile(output_dir=self.__p__.output_dir,
                           reference_filename=reference_filename,
                           output_prefix=self.__p__.output_prefix) as csv:
                if not os.path.exists(csv.output_file):
                    #check if output file for summary statistics exists already
                    with NumpyCSVFile(output_dir=self.__p__.output_dir,
                        reference_filename=reference_filename,
                        output_suffix='_sum',
                        output_prefix=self.__p__.output_prefix) as csv:
                        pass
            if os.path.exists(csv.output_file):
                message = 'Skipping processing, the outcome file ' + str(csv.output_file) + ' exists !' # @IgnorePep8
                self.__outcome_exists__ = True
                self.__info_handler__(message)
        return (True, None,) if message == None else (False, message,)

    @property
    def outcome_exists(self):
        return self.__outcome_exists__ \
                if hasattr(self, '__outcome_exists__') else False

    def generate(self, data_vector, start_progress=None,
                 progress_handler=None):
        """
        generate poincare plots
        """
        if not start_progress == None:
            if hasattr(start_progress, 'progress_mark'):
                if start_progress.progress_mark == None:
                    start_progress.progress_mark = self.__p__.progress_mark
            if hasattr(start_progress, 'info_handler'):
                if start_progress.info_handler == None:
                    start_progress.info_handler = self.__info_handler__
        return self.__generate_core__(data_vector,
                                       start_progress=start_progress,
                                       progress_handler=progress_handler)

    def generate_CSV(self, data_vector, reference_filename,
                                  start_progress=None, progress_handler=None):
        """
        generates poincare plots and saves outcomes to csv files
        """
        with NumpyCSVFile(output_dir=self.__p__.output_dir,
                    reference_filename=reference_filename,
                    output_precision=self.__p__.output_precision,
                    print_output_file=True,
                    ordinal_column_name=self.__p__.ordinal_column_name,
                    output_separator=self.__p__.output_separator,
                    sort_headers=False,
                    add_headers=self.__p__.add_headers,
                    output_prefix=self.__p__.output_prefix,
                    ordered_headers=self.__p__.statistics_names) as csv:

            if not start_progress == None:
                start_progress.reference_filename = reference_filename
                if hasattr(start_progress, 'progress_mark'):
                    if start_progress.progress_mark == None:
                        start_progress.progress_mark = self.__p__.progress_mark
                if hasattr(start_progress, 'info_handler'):
                    if start_progress.info_handler == None:
                        start_progress.info_handler = self.__info_handler__

            if not progress_handler == None:
                progress_handler.csv = csv

            not_interrupted = self.__generate_core__(data_vector,
                                        start_progress=start_progress,
                                        progress_handler=progress_handler)

        if not_interrupted:
            #if csv.info_message:
            #    self.__p__.info_handler(csv.info_message)
            if csv.error_message:
                self.__info_handler__(csv.error_message)
                return

            #give info about saved file
            if csv.saved and self.__p__.output_file_listener:
                self.__p__.output_file_listener(csv.output_file)

            if not self.__p__.summary_statistics == None:
                #get ordered headers for summary statistics
                ordered_headers = get_summary_statistics_order_for_csv(
                                    self.__p__.summary_statistics_order)
                with NumpyCSVFile(output_dir=self.__p__.output_dir,
                     reference_filename=reference_filename,
                     output_precision=self.__p__.output_precision,
                     print_output_file=True,
                     output_separator=self.__p__.output_separator,
                     sort_headers=False,
                     add_headers=self.__p__.add_headers,
                     output_suffix='_sum',
                     ordered_headers=ordered_headers,
                     output_prefix=self.__p__.output_prefix,
                     message='\nSummary statistics saved into the file: ') as summary_csv: # @IgnorePep8
                    summary_csv.write(get_summary_statistics_for_csv(
                                        self.__p__.summary_statistics))

                #give info about saved summary file
                if summary_csv.saved and self.__p__.output_file_listener:
                    self.__p__.output_file_listener(summary_csv.output_file)
        return not_interrupted

    def generate_movie(self, data_vector, reference_filename, start_progress):
        """
        generates poincare plot movie
        """
        if not start_progress == None:
            start_progress.reference_filename = reference_filename
            if hasattr(start_progress, 'progress_mark'):
                if start_progress.progress_mark == None:
                    start_progress.progress_mark = self.__p__.progress_mark
            if hasattr(start_progress, 'info_handler'):
                if start_progress.info_handler == None:
                    start_progress.info_handler = self.__info_handler__

        not_interrupted = self.__generate_movie__(data_vector,
                                    start_progress=start_progress,
                                    reference_filename=reference_filename)

        return not_interrupted

    def __generate_core__(self, data_vector, start_progress,
                          progress_handler=None):
        """
        core functionality to generate poincare plots
        """
        filter_manager = FilterManager(_shift=self.__p__.window_shift,
                    _excluded_annotations=self.__p__.excluded_annotations,
                    _filters=self.__p__.filters)

        #there could be the case when only statistics name are defined
        #and then we have to extract from the names corresponding classes
        statistics_classes = extended_statistics_classes(
                self.__p__.statistics_classes,
                self.__p__.statistics_names,
                self.__p__.summary_statistics_classes,
                self.__p__.summary_statistics_names)

        statisticsFactory = StatisticsFactory(
                    statistics_names=self.__p__.statistics_names,
                    statistics_classes=statistics_classes,
                    statistics_handlers=self.__p__.statistics_handlers,
                    _use_identity_line=self.__p__.use_identity_line,
                    use_buffer=self.__p__.use_buffer)
        if not statisticsFactory.has_statistics:
            return True
        summaryStatisticsFactory = SummaryStatisticsFactory(
            summary_statistics_names=self.__p__.summary_statistics_names,
            summary_statistics_classes=self.__p__.summary_statistics_classes)

        segmenter = SegmenterManager.getDataVectorSegmenter(data_vector,
                                            self.__p__.window_size_value,
                                            self.__p__.window_size_unit,
                                            self.__p__.sample_step,
                                            self.__p__.window_shift,
                                            self.__p__.stepper_size,
                                            self.__p__.stepper_unit)
        if self.__p__.print_first_signal:
            print('Signal data [first row]: ' + str(data_vector.signal))

        if segmenter.stop:
            return True  # to avoid interrupt processing many data sources

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
            if data_segment == None or data_segment.signal == None \
                or not len(data_segment.signal) > 1:
                parameters_old = parameters
                data_segment_old = data_segment
                continue

            #this situation could occur when there is a normal signal after
            #a long series of annotated signals
            if segmenter.data_changed:
                if len(data_segment.signal) == 1:
                    continue

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

        self.__p__.summary_statistics = None
        if interrupter.isInterrupted() == False:
            if summaryStatisticsFactory.has_summary_statistics > 0:
                self.__p__.summary_statistics = summaryStatisticsFactory.summary_statistics # @IgnorePep8
                self.__p__.summary_statistics_order = summaryStatisticsFactory.summary_statistics_order # @IgnorePep8

        if progress:
            close = getattr(progress, 'close')
            if close:
                close()
        interrupted = interrupter.isInterrupted()
        interrupter.clean()

        return not interrupted

    def __default_info_handler__(self, info):
        if not info == None:
            print('\n' + info)

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
                                            self.__p__.output_precision)
        return formatted_statistics

    def segment_count(self, data_vector):
        """
        calculates approximate number of segments count during
        processing of poincare plot
        """
        segmenter = SegmenterManager.getDataVectorSegmenter(data_vector,
                                            self.__p__.window_size_value,
                                            self.__p__.window_size_unit,
                                            self.__p__.sample_step,
                                            self.__p__.window_shift,
                                            self.__p__.stepper_size,
                                            self.__p__.stepper_unit)
        return segmenter.segment_count()

    def __generate_movie__(self, data_vector, start_progress,
                           reference_filename):
        """
        core functionality to generate poincare plot movie
        """
        filter_manager = FilterManager(_shift=self.__p__.window_shift,
                    _excluded_annotations=self.__p__.excluded_annotations,
                    _filters=self.__p__.filters)

        segmenter = SegmenterManager.getDataVectorSegmenter(data_vector,
                                            self.__p__.window_size_value,
                                            self.__p__.window_size_unit,
                                            self.__p__.sample_step,
                                            self.__p__.window_shift,
                                            self.__p__.stepper_size,
                                            self.__p__.stepper_unit,
                                            mark_last_segment=True)
        if segmenter.stop:
            return True  # to avoid interrupt processing many data sources

        start_progress.segmenter = segmenter
        start_progress()
        progress = start_progress.progress
        if progress == False:
            return False

        interrupter = ControlInterruptHandler()
        data_segment_old = None

        self.__movie_progress__ = progress

        movie_maker = PoincarePlotMovieMaker(data_vector, self.__p__,
                            segment_count=segmenter.segment_count(),
                            filter_manager=filter_manager,
                            info_message_handler=self.__info_message_handler__,
                            reference_filename=reference_filename)

        for data_segment in segmenter:
            if segmenter.last_segment:
                movie_maker.add_data_vector_segment(None, last_segment=True)
                break

            if interrupter.isInterrupted():
                #mark interrupt state of interrupter to give consistent
                #behaviour to the rest of the code
                interrupter.interrupt()
                break

            if segmenter.data_changed:
                data_segment = filter_manager.run_filters(data_segment)

            #this could happened when for example annotation
            #filter is used and all data are annotated that means
            #all signal data are filtered out
            if data_segment == None or data_segment.signal == None \
                or not len(data_segment.signal) > 1:
                data_segment_old = data_segment
                continue

            #this situation could occur when there is a normal signal after
            #a long series of annotated signals
            if segmenter.data_changed:
                if len(data_segment.signal) == 1:
                    continue

            if segmenter.data_changed and \
                not data_segment.equals(data_segment_old):
                movie_maker.add_data_vector_segment(data_segment)
                progress.tick(additional_message=movie_maker.info_message)

            data_segment_old = data_segment

        progress.close()
        interrupted = interrupter.isInterrupted()
        interrupter.clean()

        if not interrupted or self.__p__.movie_save_partial:
            movie_maker.save_movie()
            self.__info_handler__(movie_maker.info_message)

        self.__movie_progress__ = None

        return not interrupted

    def __info_message_handler__(self, _message):
        if not self.__movie_progress__ == None:
            self.__movie_progress__.tick(additional_message=_message)
        else:
            self.__info_handler__(_message)


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
            self.info_handler("Window size can't be greater then data size !!!") # @IgnorePep8
            self.__progress__ = False
            return False
        return True

    def __call__(self):
        if self.check():
            if self.progress_mark:
                self.__progress__ = ProgressMark(_label='Processing data...',
                                _max_count=self.segmenter.segment_count())
            else:
                self.info_handler('Processing data')

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


class MovieStartProgressGenerator(StartProgressGenerator):
    """
    callable class used when a movie is about to be created
    """
    def __call__(self):
        if self.check():
            self.__progress__ = ProgressMark(
                            _label='Processing file ' +
                            self.reference_filename + ' ...',
                            _max_count=self.segmenter.segment_count())
