'''
Created on 27-07-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import os
    import argparse
    import glob
    from pycore.misc import Separator
    from pycore.utils import ProgressMark
    from pycore.utils import ControlInterruptHandler
    from pycore.introspection import copy_private_properties
    from pycore.introspection import print_private_properties
    from pycore.collections_utils import nvl
    from pycore.collections_utils import commas
    from pymath.model.file_data_source import FileDataSource
    from pymath.model.data_vector_segmenter import DataVectorSegmenter
    from pymath.model.data_vector_parameters import DataVectorParameters
    from pymath.model.file_data_parameters import FileDataParameters
    from pymath.statistics.statistic_parameters import StatisticParameters
    from pymath.frequency_domain.fourier_parameters import FourierParameters
    from pymath.time_domain.poincare_plot.poincare_plot_parameters import PoincarePlotParameters # @IgnorePep8
    from pymath.time_domain.poincare_plot.filters.filter_parameters import FilterParameters # @IgnorePep8
    from pymath.utils.io_utils import NumpyCSVFile
    from pymath.statistics.statistics import StatisticsFactory
    from pymath.statistics.statistics import get_statistics_names
    from pymath.statistics.statistics import ALL_STATISTICS
    from pymath.statistics.summary_statistics import get_summary_statistics_names # @IgnorePep8
    from pymath.statistics.summary_statistics import ALL_SUMMARY_STATISTICS
    from pymath.statistics.summary_statistics import SummaryStatisticsFactory
    from pymath.frequency_domain.fourier_parameters import getInterpolationNames # @IgnorePep8
    from pymath.frequency_domain.fourier import FourierTransformationManager
    from pymath.frequency_domain.fourier_parameters import getFourierTransformationNames # @IgnorePep8
    from pymath.time_domain.poincare_plot.filters.filter_utils import get_filters_short_names # @IgnorePep8
    from pymath.time_domain.poincare_plot.filters.filter_manager import FilterManager # @IgnorePep8
except ImportError as error:
    print_import_error(__name__, error)


DEFAULT_OUTCOME_DIRECTORY = os.path.join(os.getcwd(), 'pp_outcomes')


def getSeparatorLabels():
    """
    to get default separator label names
    """
    return commas(Separator.getSeparatorsLabels())


class PoincarePlotManager(PoincarePlotParameters, DataVectorParameters,
                          FileDataParameters, FilterParameters,
                          StatisticParameters, FourierParameters):
    def __init__(self, other=None):
        PoincarePlotParameters.__init__(self)
        DataVectorParameters.__init__(self)
        FileDataParameters.__init__(self)
        FilterParameters.__init__(self)
        StatisticParameters.__init__(self)
        FourierParameters.__init__(self)

        self.__progress_mark__ = None
        if not other == None:
            copy_private_properties(other, self)

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    def generate(self):
        """
        the method which starts to generate Poincare Plot parameters into
        output files, names of the output files are the same as input files
        plus '_out' suffix
        """
        if self.__check__():
            self.__print_information__()
            self.__process__(self.__process_file__)

    def __process__(self, _file_handler, disp=True, **params):
        """
        the method which starts to generate Poincare Plot parameters
        """
        sign_multiplicator = 80
        file_counter = 0
        if disp:
            print('*' * sign_multiplicator)
        if self.data_file:  # data_file parameter is superior to data_dir parameter @IgnorePep8
            if os.path.exists(self.data_file) == False:
                if disp:
                    print('The file: ' + self.data_file + " doesn't exist")
            else:
                file_counter = 1
                _file_handler(self.data_file, disp=disp, **params)
        else:
            path = self.data_dir + ('*.*'
                            if self.extension == None else self.extension)
            for _file in glob.glob(path):
                if os.path.isfile(_file):
                    file_counter = file_counter + 1
                    if disp:
                        print('=' * sign_multiplicator)
                    _file_handler(_file, disp=disp, **params)
        if disp:
            print('Processing finished')
            if file_counter == 0:
                print('No files to process [' + self.data_dir
                                            + self.extension + ']')
            else:
                print('Number of processed files: ' + str(file_counter))

    def __process_file__(self, _file, disp=False):
        file_data_source = FileDataSource(_file=_file,
                               signal_index=self.signal_index,
                               annotation_index=self.annotation_index,
                               time_index=self.time_index)
        data_vector = file_data_source.getData()
        parameters = {}
        fourier = FourierTransformationManager(self.fourier_transformation,
                                    self.fourier_transform_interpolation)
        filter_manager = FilterManager(_shift=self.window_shift,
                        _excluded_annotations=self.excluded_annotations,
                        _filters=self.filters)
        with NumpyCSVFile(output_dir=self.output_dir,
                         reference_filename=_file,
                         output_precision=self.output_precision,
                         print_output_file=True,
                         ordinal_column_name=self.ordinal_column_name,
                         output_separator=self.output_separator,
                         sort_headers=False,
                         output_headers=self.output_headers,
                         ordered_headers=self.statistics) as csv:
            summaryStatisticsFactory = SummaryStatisticsFactory(
                                                    self.summary_statistics)
            if self.skip_existing_outcomes:
                #only used to check if summary output file exists
                if summaryStatisticsFactory.has_summary_statistics > 0:
                    summary_csv = NumpyCSVFile(output_dir=self.output_dir,
                                           reference_filename=_file,
                                           output_suffix='_sum')
                    if os.path.exists(summary_csv.output_file):
                        if disp:
                            print('Skipping processing, the summary outcome file ' # @IgnorePep8
                                  + str(summary_csv.output_file) + ' exists !')
                            return

                if os.path.exists(csv.output_file):
                    if disp:
                        print('Skipping processing, the outcome file '
                              + str(csv.output_file) + ' exists !')
                    return
            statisticsFactory = StatisticsFactory(self.statistics,
                            statistics_handlers=self.__statistics_handlers__,
                            _use_identity_line=self.use_identity_line,
                            use_buffer=self.use_buffer)
            if not statisticsFactory.has_statistics:
                return
            segmenter = DataVectorSegmenter(data_vector,
                                    self.window_size,
                                    shift=self.window_shift,
                                    window_size_unit=self.window_size_unit)
            progress = None
            segment_count = segmenter.segment_count()
            if disp:
                if self.progress_mark:
                    progress = ProgressMark(_label='Processing file ' + _file
                                             + ' ...',
                                        _max_count=segment_count)
                else:
                    print('Processing file: ' + _file)
            if segment_count == -1:
                if disp:
                    print("Window size can't be greater then data size !!!")
                return

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

            if summaryStatisticsFactory.has_summary_statistics > 0:
                summary_headers = \
                            summaryStatisticsFactory.summary_statistics.keys()
                #save summary statistics into a file
                with NumpyCSVFile(output_dir=self.output_dir,
                         reference_filename=_file,
                         output_precision=self.output_precision,
                         print_output_file=True,
                         output_separator=self.output_separator,
                         sort_headers=False,
                         output_headers=summary_headers,
                         output_suffix='_sum',
                         message='\nSummary statistics saved into the file: ') as summary_csv: # @IgnorePep8 
                    summary_csv.write(summaryStatisticsFactory.summary_statistics) # @IgnorePep8

            if progress:
                progress.close
            interrupter.clean()

    def getUniqueAnnotations(self):
        """
        [optional]
        display unique annotation values included in input files;
        warning: data_dir or data_file and annotation_index have to be set up
        """
        unique_annotations = []
        self.__process__(self.__process_annotations__, disp=False,
                         _unique_annotations=unique_annotations)
        return set(unique_annotations)

    def __process_annotations__(self, _file, _unique_annotations=None):
        file_data_source = FileDataSource(_file=_file,
                                annotation_index=self.annotation_index)
        _unique_annotations[len(_unique_annotations):] = \
                    file_data_source.getUniqueAnnotations()

    def getHeaders(self, with_col_index=True):
        """
        [optional]
        display lines of headers of input files;
        warning: data_dir or data_file has to be set up
        """
        headers = []
        self.__process__(self.__process_headers__, disp=False,
                         _headers=headers)
        return headers

    def __process_headers__(self, _file, _headers=None):
        file_data_source = FileDataSource(_file=_file)
        _headers.append('File: ' + str(_file))
        _headers.append(file_data_source.headers_with_col_index)

    def __check__(self):
        if self.statistics == None or len(self.statistics) == 0:
            print('no statistics were been chosen [attribute statistics];')
            print('available statistics [call method available_statistics()]:')
            self.available_statistics()
        elif self.data_file is None and self.data_dir is None:
            print('data_file or data_dir have to be set')
        elif self.output_dir is None:
            print('output_dir has to be set')
        elif self.window_size is None:
            print('window size has to be set')
        elif self.signal_index is None:
            print('signal index has to be set')
        else:
            return True
        return False

    @property
    def progress_mark(self):
        """
        [optional]
        whether a progress mark have to be displayed during processing files
        default False
        """
        return self.__progress_mark__

    @progress_mark.setter
    def progress_mark(self, _progress_mark):
        self.__progress_mark__ = _progress_mark

    def print_members(self):
        """
        [optional]
        prints members values
        """
        print_private_properties(self)
        print('\n available statistics:')
        self.available_statistics()

    def __print_information__(self):
        print('Using statistics: ' + self.statistics)
        if self.__statistics_handlers__:
            print('Using statistics handlers/functions:')
            for _handler in self.__statistics_handlers__:
                print('   name: ' + _handler.name)
        if self.summary_statistics:
            print('Using summary statistics: ' + self.summary_statistics)
        print('Using output precision: ' + self.output_precision)
        print('Using buffer: ' + str(self.use_buffer))
        if not self.filters_names == None:
            print('Using filters: ' + str(self.filters_names))
        print('Window size: ' + str(self.window_size) +
              nvl(self.window_size_unit, ''))
        print('Using buffer: ' + str(self.use_buffer))
        print('Skip for existing outcomes: '
              + str(self.skip_existing_outcomes))


if __name__ == '__main__':
    to_bool = lambda p: True if p.title() == "True" else False

    parser = argparse.ArgumentParser('Program to generate Poincare Plot parameters:') # @IgnorePep8
    parser.add_argument("-i", "--interactive",
                help="interactive mode (not implemented yet)", type=to_bool,
                default=False)
    parser.add_argument("-d", "--data_dir",
                help="directory where input data files are located [default: " + os.getcwd() + "]", # @IgnorePep8
                default=os.getcwd())
    parser.add_argument("-e", "--extension", default="*",
                help="extension of data input files in the form <*.ext>")
    parser.add_argument("-f", "--data_file",
                help="alternative option to set one data source file")
    parser.add_argument("-w", "--window_size",
                help="""data window size expressed in number of data items or
                in time units by suffix: s - second, m - minute, h - hour;
                examples: 100, 5m""")
    parser.add_argument("-ws", "--window_shift", type=int,
                help="window data shift between two sets of signals",
                default=1)
    parser.add_argument("-o", "--output_dir",
                help="directory for outcomes files [default: " +
                        DEFAULT_OUTCOME_DIRECTORY + "]",
                default=DEFAULT_OUTCOME_DIRECTORY)
    parser.add_argument("-out_prec", "--output_precision",
                help="precision for output data [default: 10,5]",
                default="10,5")
    parser.add_argument("-s", "--statistics",
                help="list of statistics names to calculate, available: " +
                        commas(get_statistics_names(ALL_STATISTICS)))
    parser.add_argument("-ss", "--summary_statistics",
                help="list of summary statistics names to calculate, available: " + # @IgnorePep8
                commas(get_summary_statistics_names(ALL_SUMMARY_STATISTICS)))
    parser.add_argument("-he", "--headers", type=to_bool,
                        help="display lines of headers [True|False]")
    parser.add_argument("-si", "--signal_index", type=int,
                help="index of a signal column in a data source file (0 based)", # @IgnorePep8
                default=-1)
    parser.add_argument("-ai", "--annotation_index", type=int,
                help="index of an annotation column in a data source file (0 based)", # @IgnorePep8
                default=-1)
    parser.add_argument("-ti", "--time_index", type=int,
                help="index of a time column in a data source file (0 based)" +
                    " [for future use]",
                default=-1)
    parser.add_argument("-p", "--separator",
                help="a separator used between columns, one from the set: " +
                     getSeparatorLabels() + ", <custom>; note: the " +
                     "application tries to discover a separator itself")
    parser.add_argument("-dav", "--display_annotation_values",
                help="display unique annotations values presented in " +
                    "data source files [True|False]",
                type=to_bool, default=False)
#    parser.add_argument("-df", "--display_filters",
#                help="display list of available filters [True|False]",
#                type=to_bool, default=False)
    parser.add_argument("-fts", "--filters_names",
                help="""use filters; available filters: """
                    + commas(get_filters_short_names()))
    parser.add_argument("-ft", "--fourier_transformation",
                help="""use fourier transformation; available: """ +
                        getFourierTransformationNames())
    parser.add_argument("-fti", "--fourier_transform_interpolation",
                help="""use interpolation method during fourier transformation
                    ; available interpolations: """ + getInterpolationNames())
    parser.add_argument("-ea", "--excluded_annotations",
                help="""specifies which values (separated by a comma) have to
                         be interpreted as true annotations values;
                         if not specified then all non-0 values in a annotation
                         column are such entities""")
    parser.add_argument("-ordinal", "--ordinal_column_name",
                help="""name of the ordinal column, index or time it depends
                 on window size unit, which will be the first column
                 in outcomes""")  # @IgnorePep8
    parser.add_argument("-out_sep", "--output_separator",
                help="a separator for output data [default: ',']",
                default=",")
    parser.add_argument("-out_headers", "--output_headers",
                help="headers in the output files [default: True]",
                type=to_bool, default=True)
    parser.add_argument("-uil", "--use_identity_line",
                help="during calculations use identity line [True|False]",
                type=to_bool, default=True)
    parser.add_argument("-ub", "--use_buffer",
            help="use buffer during statistics calculations [default: True]",
            type=to_bool, default=True)
    parser.add_argument("-seo", "--skip_existing_outcomes",
                help="skip processing data file if there are corresponding \
                        outcome files [True|False]",
                type=to_bool, default=True)
    __args = parser.parse_args()

    ppManager = PoincarePlotManager()
    ppManager.data_file = __args.data_file
    ppManager.data_dir = __args.data_dir
    ppManager.extension = __args.extension
    ppManager.window_size = __args.window_size
    ppManager.window_shift = __args.window_shift
    ppManager.output_dir = __args.output_dir
    ppManager.statistics = __args.statistics
    ppManager.summary_statistics = __args.summary_statistics
    ppManager.signal_index = __args.signal_index
    ppManager.annotation_index = __args.annotation_index
    ppManager.time_index = __args.time_index
    ppManager.output_precision = __args.output_precision
    ppManager.filters_names = __args.filters_names
    ppManager.fourier_transformation = \
                    __args.fourier_transformation
    ppManager.fourier_transform_interpolation = \
                    __args.fourier_transform_interpolation
    ppManager.excluded_annotations = __args.excluded_annotations
    ppManager.ordinal_column_name = __args.ordinal_column_name
    ppManager.output_separator = __args.output_separator
    ppManager.output_headers = __args.output_headers
    ppManager.use_identity_line = __args.use_identity_line
    ppManager.skip_existing_outcomes = __args.skip_existing_outcomes
    ppManager.use_buffer = __args.use_buffer
    _disp = False
    #ppManager.addStatisticHandler(stat_double)
    if __args.display_annotation_values == True:
        _disp = True
        print('Annotations: ' + commas(ppManager.getUniqueAnnotations(),
                                       _default='none'))
#    if __args.display_filters == True:
#        _disp = True
#        print('Filters: ' + get_filters_short_names())
    if __args.headers == True:
        _disp = True
        print('Headers:')
        for header in ppManager.getHeaders():
            print(header)
    if _disp == False:
        ppManager.generate()
