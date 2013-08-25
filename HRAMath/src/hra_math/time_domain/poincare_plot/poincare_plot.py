'''
Created on 27-07-2012

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import os
    import argparse
    import glob
    from hra_core.datetime_utils import invocation_time
    from hra_core.misc import Separator
    from hra_core.introspection import copy_private_properties
    from hra_core.introspection import print_private_properties
    from hra_core.collections_utils import commas
    from hra_math.model.data_vector_file_data_source import DataVectorFileDataSource # @IgnorePep8
    from hra_math.model.data_vector_parameters import DataVectorParameters
    from hra_math.model.file_data_parameters import FileDataParameters
    from hra_math.statistics.statistic_parameters import StatisticParameters
    from hra_math.time_domain.poincare_plot.poincare_plot_parameters import PoincarePlotParameters # @IgnorePep8
    from hra_math.time_domain.poincare_plot.filters.filter_parameters import FilterParameters # @IgnorePep8
    from hra_math.time_domain.poincare_plot.poincare_plot_movie_parameters import PoincarePlotMovieParameters # @IgnorePep8
    from hra_math.statistics.statistics import get_statistics_names
    from hra_math.statistics.statistics import ALL_STATISTICS
    from hra_math.statistics.summary_statistics import get_summary_statistics_names # @IgnorePep8
    from hra_math.statistics.summary_statistics import ALL_SUMMARY_STATISTICS
    from hra_math.time_domain.poincare_plot.filters.filter_utils import get_filters_short_names # @IgnorePep8
    from hra_math.time_domain.poincare_plot.poincare_plot_generator \
        import PoincarePlotGenerator
    from hra_math.time_domain.poincare_plot.poincare_plot_generator \
        import CSVStartProgressGenerator
    from hra_math.time_domain.poincare_plot.poincare_plot_generator \
        import CSVProgressHandlerGenerator
    from hra_math.time_domain.poincare_plot.poincare_plot_generator \
        import MovieStartProgressGenerator
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
                          StatisticParameters,
                          PoincarePlotMovieParameters):
    def __init__(self, other=None):
        PoincarePlotParameters.__init__(self)
        DataVectorParameters.__init__(self)
        FileDataParameters.__init__(self)
        FilterParameters.__init__(self)
        StatisticParameters.__init__(self)
        PoincarePlotMovieParameters.__init__(self)

        self.__progress_mark__ = None
        if not other == None:
            copy_private_properties(other, self)

        self.__pp_generator__ = None

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    def generate(self):
        self.__pp_generator__ = PoincarePlotGenerator(
                                        file_data_parameters=self,
                                        data_vector_parameters=self,
                                        filter_parameters=self,
                                        statistic_parameters=self,
                                        poincare_plot_parameters=self)
        message = self.__pp_generator__.checkParameters()
        if message:
            print(message)
            return
        self.__pp_generator__.parameters_info

        self.__process__(self.__process_file__)

    def generate_movie(self):
        self.__pp_generator__ = PoincarePlotGenerator(
                                        file_data_parameters=self,
                                        data_vector_parameters=self,
                                        filter_parameters=self,
                                        poincare_plot_parameters=self,
                                        poincare_plot_movie_parameters=self)
        message = self.__pp_generator__.checkParameters()
        if message:
            print(message)
            return
        self.__pp_generator__.parameters_info

        self.__process__(self.__process_file_for_movie__)

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
                    if _file_handler(_file, disp=disp, **params) == False:
                        break
        if disp:
            print('Processing finished')
            if file_counter == 0:
                print('No files to process [' + self.data_dir
                                            + self.extension + ']')
            else:
                print('Number of processed files: ' + str(file_counter))

    @invocation_time
    def __process_file__(self, _file, disp=False):
        file_data_source = DataVectorFileDataSource(_file=_file,
                               signal_index=self.signal_index,
                               annotation_index=self.annotation_index,
                               time_index=self.time_index)
        data_vector = file_data_source.getDataVector()

        (ok, message) = self.__pp_generator__.precheck(reference_filename=_file) # @IgnorePep8
        if ok == False:
            if disp:
                print('\n' + message)
            return True

        start_progress = CSVStartProgressGenerator()
        start_progress.progress_mark = self.progress_mark
        start_progress.info_handler = self.info_handler
        return self.__pp_generator__.generate_CSV(data_vector, _file,
                            start_progress=start_progress,
                            progress_handler=CSVProgressHandlerGenerator())

    @invocation_time
    def __process_file_for_movie__(self, _file, disp=False):
        file_data_source = DataVectorFileDataSource(_file=_file,
                               signal_index=self.signal_index,
                               annotation_index=self.annotation_index,
                               time_index=self.time_index)
        data_vector = file_data_source.getDataVector()

        start_progress = MovieStartProgressGenerator()
        start_progress.progress_mark = self.progress_mark
        start_progress.info_handler = self.info_handler
        return self.__pp_generator__.generate_movie(data_vector, _file,
                                                start_progress=start_progress)

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
        file_data_source = DataVectorFileDataSource(_file=_file,
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
        file_data_source = DataVectorFileDataSource(_file=_file)
        _headers.append('File: ' + str(_file))
        _headers.append(file_data_source.headers_with_col_index)

    def print_members(self):
        """
        [optional]
        prints members values
        """
        print_private_properties(self)
        print('\n available statistics:')
        self.available_statistics()

    def info_handler(self, _message):
        print(_message)


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
    parser.add_argument("-sn", "--statistics_names",
                help="list of statistics names to calculate, available: " +
                        commas(get_statistics_names(ALL_STATISTICS)))
    parser.add_argument("-ssn", "--summary_statistics_names",
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
    parser.add_argument("-fts", "--filters_names",
                help="""use filters; available filters: """
                    + commas(get_filters_short_names()))
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
    parser.add_argument("-add_headers", "--add_headers",
                help="headers in the output files [default: True]",
                type=to_bool, default=True)
    parser.add_argument("-uil", "--use_identity_line",
                help="during calculations use identity line [True|False]",
                type=to_bool, default=True)
    parser.add_argument("-ub", "--use_buffer",
            help="use buffer during statistics calculations [default: True]",
            type=to_bool, default=True)
    parser.add_argument("-override", "--override_existing_outcomes",
                help="override existing outcomes [True|False]",
                type=to_bool, default=False)
    parser.add_argument("-sample", "--sample_step",
            help="""how big have to be a step for window resampling size;
                it is assumed that this quantity is expressed in signal unit
                value 0 means no use of window resampling size at all
                [optional]""",
            type=int)
    parser.add_argument("-stepper", "--stepper",
                help="""to define amount by which data window have to jump
                during process of data expressed in number of data items
                or in time units by suffix: s - second, m - minute, h - hour;
                examples: 100, 5m [optional]""")
    parser.add_argument("-movie_name", "--movie_name",
                help="""name of a movie for Poincare plot evolutions""")
    parser.add_argument("-movie_dir", "--movie_dir",
                help="directory for movie files [default: " +
                        DEFAULT_OUTCOME_DIRECTORY + "]",
                default=DEFAULT_OUTCOME_DIRECTORY)
    parser.add_argument("-multi_proc_factor", "--movie_multiprocessing_factor",
                help="""to generate a poincare plot movie use multiprocessing,
                 active on multiprocessing hardware, greater value > 0 give
                 use more of processors
                 """, type=int)
    parser.add_argument("-movie_bin_size", "--movie_bin_size",
                help="""movie bin size """, type=int)
    parser.add_argument("-fps", "--movie_fps",
                help="""a movie fps [optional]""", type=int)
    parser.add_argument("-movie_skip_to_frame", "--movie_skip_to_frame",
                help="""skip to a movie frame [optional]""", type=int)
    parser.add_argument("-movie_experimental_code",
                        "--movie_experimental_code",
                help="""use some movie experimental code;
                         only for tests, default False""",
                type=to_bool, default=False)
    parser.add_argument("-movie_animated", "--movie_animated",
                help="""use animation API to generate a movie;
                        required mencoder and ffmpeg [default False]""",
                type=to_bool, default=False)
    __args = parser.parse_args()

    ppManager = PoincarePlotManager()
    ppManager.data_file = __args.data_file
    ppManager.data_dir = __args.data_dir
    ppManager.extension = __args.extension
    ppManager.window_size = __args.window_size
    ppManager.window_shift = __args.window_shift
    ppManager.output_dir = __args.output_dir
    ppManager.statistics_names = __args.statistics_names
    ppManager.summary_statistics_names = __args.summary_statistics_names
    ppManager.signal_index = __args.signal_index
    ppManager.annotation_index = __args.annotation_index
    ppManager.time_index = __args.time_index
    ppManager.output_precision = __args.output_precision
    ppManager.filters_names = __args.filters_names
    ppManager.excluded_annotations = __args.excluded_annotations
    ppManager.ordinal_column_name = __args.ordinal_column_name
    ppManager.output_separator = __args.output_separator
    ppManager.add_headers = __args.add_headers
    ppManager.use_identity_line = __args.use_identity_line
    ppManager.override_existing_outcomes = __args.override_existing_outcomes
    ppManager.use_buffer = __args.use_buffer
    ppManager.sample_step = __args.sample_step
    ppManager.stepper = __args.stepper
    ppManager.movie_name = __args.movie_name
    ppManager.movie_dir = __args.movie_dir
    ppManager.movie_multiprocessing_factor = \
                    __args.movie_multiprocessing_factor
    ppManager.movie_fps = __args.movie_fps
    ppManager.movie_bin_size = __args.movie_bin_size
    ppManager.movie_skip_to_frame = __args.movie_skip_to_frame
    ppManager.movie_experimental_code = __args.movie_experimental_code
    ppManager.movie_animated = __args.movie_animated
    _disp = False
    if __args.display_annotation_values == True:
        _disp = True
        print('Annotations: ' + commas(ppManager.getUniqueAnnotations(),
                                       _default='none'))
    if __args.headers == True:
        _disp = True
        print('Headers:')
        for header in ppManager.getHeaders():
            print(header)
    if _disp == False:
        if ppManager.movie_name == None:
            ppManager.generate()
        else:
            ppManager.generate_movie()
