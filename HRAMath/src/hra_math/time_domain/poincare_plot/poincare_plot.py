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
    from hra_core.introspection import print_private_properties
    from hra_core.introspection import copy_object
    from hra_core.collections_utils import commas
    from hra_core.collections_utils import nvl
    from hra_core.io_utils import join_files
    from hra_core.io_utils import as_path
    from hra_core.io_utils import create_dir
    from hra_math.utils.io_utils import shuffle_file
    from hra_math.model.data_vector_file_data_source \
        import DataVectorFileDataSource
    from hra_math.model.parameters.poincare_plot_parameters \
        import PoincarePlotParameters
    from hra_math.model.parameters.poincare_plot_parameters \
        import COMMON_PARAMETERS_GROUP
    from hra_math.model.parameters.poincare_plot_parameters \
        import MOVIE_PARAMETERS_GROUP
    from hra_math.model.parameters.poincare_plot_parameters \
        import STATISTICS_PARAMETERS_GROUP
    from hra_math.statistics.statistics import get_statistics_names
    from hra_math.statistics.statistics import ALL_STATISTICS
    from hra_math.statistics.summary_statistics \
        import get_summary_statistics_names
    from hra_math.statistics.summary_statistics \
        import ALL_SUMMARY_STATISTICS
    from hra_math.time_domain.poincare_plot.filters.filter_utils \
        import get_filters_short_names
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


class PoincarePlotManager(object):

    def __init__(self):
        self.__p__ = PoincarePlotParameters()
        self.__progress_mark__ = None
        self.__pp_generator__ = None

    def __getattr__(self, name):
        """
        if attribute starts and ends with two underscores
        belongs to self object, otherwise to self.__p__ member
        """
        if name.startswith('__') and name.endswith('__'):
            return self.__dict__[name]
        else:
            return getattr(self.__dict__['__p__'], name)

    def __setattr__(self, name, value):
        """
        if attribute starts and ends with two underscores
        sets for self object otherwise for self.__p__ member
        """
        if name.startswith('__') and name.endswith('__'):
            self.__dict__[name] = value
        else:
            setattr(self.__dict__['__p__'], name, value)

    def generate(self):
        if self.__p__.parameters_info_count == 0:
            self.getParser()
        self.__p__.prepareParameters()
        self.__save_members__()
        self.__pp_generator__ = PoincarePlotGenerator(parameters=self.__p__)
        message = self.__p__.validateParameters()
        if message:
            print(message)
            return
        self.info(valued_only=True)
        self.__process__(self.__process_file__)

    def generate_movie(self):
        if self.__p__.parameters_info_count == 0:
            self.getParser()
        self.__p__.prepareParameters()
        self.__save_members__()
        self.__pp_generator__ = PoincarePlotGenerator(parameters=self.__p__)
        message = self.__p__.validateParameters()
        if message:
            print(message)
            return
        self.info(valued_only=True)
        self.__process__(self.__process_file_for_movie__)

    def __process__(self, _file_handler, disp=True, **params):
        """
        the method which starts to generate Poincare Plot parameters
        """
        sign_multiplicator = 80
        file_counter = 0
        if disp:
            print('*' * sign_multiplicator)

        if self.group_data_filename and self.data_file == None:
            #create a group data input file
            outfilename = as_path(self.output_dir,
                                  "grp_" + self.group_data_filename)
            joined = join_files(self.__data_filenames__(),
                                    headers_count=self.headers_count,
                                    outfilename=outfilename)
            if joined:
                self.data_file = outfilename
                if disp:
                    print('Using group data file: ' + self.data_file)

        if self.data_file:  # data_file parameter is superior to data_dir parameter @IgnorePep8
            _data_file = self.__shuffle_file__(self.data_file)
            if os.path.exists(_data_file) == False:
                if disp:
                    print('The file: ' + _data_file + " doesn't exist")
            else:
                file_counter = 1
                if self.__p__.check_data_indexes(_data_file, disp):
                    _file_handler(_data_file, disp=disp, **params)
        else:
            for _file in self.__data_filenames__():
                if os.path.isfile(_file):
                    file_counter = file_counter + 1
                    if disp:
                        print('=' * sign_multiplicator)
                    if not self.__p__.check_data_indexes(_file, disp):
                        continue
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
        if disp:
            if self.shuffle_data:
                print('Processing shuffled file: ' + str(_file) + '\n')
            else:
                print('Processing file: ' + str(_file) + '\n')
        file_data_source = DataVectorFileDataSource(_file=_file,
                               signal_index=self.signal_index,
                               annotation_index=self.annotation_index,
                               time_index=self.time_index,
                               headers_count=self.headers_count,
                               time_format=self.time_format,
                               separator=self.separator)
        data_vector = file_data_source.getDataVector()
        if data_vector.is_empty:
            if disp:
                print('No signal data or all data is skipped, check signal or time data columns !') # @IgnorePep8
            return True

        (ok, message) = self.__pp_generator__.precheck(reference_filename=_file) # @IgnorePep8
        if ok == False:
            if disp:
                print('\n' + message)
            return True

        start_progress = CSVStartProgressGenerator()
        start_progress.progress_mark = self.progress_mark
        start_progress.info_handler = self.info_handler
        start_progress.shuffle_data = self.shuffle_data
        return self.__pp_generator__.generate_CSV(data_vector, _file,
                            start_progress=start_progress,
                            progress_handler=CSVProgressHandlerGenerator())

    @invocation_time
    def __process_file_for_movie__(self, _file, disp=False):
        file_data_source = DataVectorFileDataSource(_file=_file,
                               signal_index=self.signal_index,
                               annotation_index=self.annotation_index,
                               time_index=self.time_index,
                               headers_count=self.headers_count,
                               time_format=self.time_format,
                               separator=self.separator)
        data_vector = file_data_source.getDataVector()
        if data_vector.is_empty:
            return True

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
        print_private_properties(self.__p__)
        print('\n available statistics:')
        self.__p__.available_statistics()

    def info_handler(self, _message):
        print(_message)

    def __data_filenames__(self):
        """
        returns all data files according to data_dir and extension
        """
        if self.data_dir:
            path = self.data_dir + nvl(self.extension, '*.*')
            return [self.__shuffle_file__(_file) for _file in glob.glob(path)]

    def save_parameters(self, _save_parameters):
        self.__save_parameters__ = _save_parameters

    def __save_members__(self):
        """
        [optional]
        save members values
        """
        if self.save_parameters:
            _filename = as_path(self.output_dir, "pp_parameters.txt")
            create_dir(self.output_dir)
            with open(_filename, 'w') as _file:
                for info_line in self.__p__.get_infos_lines(valued_only=True):
                    _file.write(info_line + "\n")
                print('Poincare plot parameters saved into a file: %s '
                      % (_filename))

    def info(self, valued_only=False):
        """
        display information about available parameters
        """
        if self.__p__.parameters_info_count == 0:
            self.getParser()
        self.__p__.info(valued_only=valued_only)

    def __shuffle_file__(self, _file):
        if self.shuffle_data:
            return shuffle_file(_file, output_dir=self.output_dir,
                                headers_count=self.headers_count)
        else:
            return _file

    def getParser(self):
        """
        parse program's parameters, the information is stored in
        poincare plot parameters object
        """
        to_bool = lambda p: True if p.title() == "True" else False

        parser = argparse.ArgumentParser('Program to generate Poincare Plot statistics:') # @IgnorePep8

        common_group = parser.add_argument_group(
                            title=COMMON_PARAMETERS_GROUP,
                            description="Common parameters")
        common_group.add_argument("-interactive", "--interactive",
            help="interactive mode (not implemented yet)", type=to_bool,
            default=False)
        common_group.add_argument("-data_dir", "--data_dir",
            help="directory where input data files are located",
            default=os.getcwd())
        common_group.add_argument("-extension", "--extension", default="*",
            help="extension of data input files in the form <*.ext>")
        common_group.add_argument("-data_file", "--data_file",
            help="alternative option to set one data source file")
        common_group.add_argument("-window_size", "--window_size",
            help="""data window size expressed in number of data items or in time units by suffix: s - second, m - minute, h - hour, examples: 100, 5m""") # @IgnorePep8
        common_group.add_argument("-ws", "--window_shift", type=int,
            help="window data shift between two sets of signals",
            default=1)
        common_group.add_argument("-output_dir", "--output_dir",
            help="directory for outcomes files",
            default=DEFAULT_OUTCOME_DIRECTORY)
        common_group.add_argument("-he", "--headers", type=to_bool,
            help="display lines of headers",
            default=False)
        common_group.add_argument("-signal_index", "--signal_index", type=int,
            help="index of a signal column in a data source file (0 based)",
            default=-1)
        common_group.add_argument("-annotation_index", "--annotation_index",
            help="""index of an annotation column in a data source file (0 based)""", # @IgnorePep8
            default=-1, type=int)
        common_group.add_argument("-time_index", "--time_index", type=int,
            help="index of a time column in a data source file (0 based)",
            default=-1)
        common_group.add_argument("-signal_label", "--signal_label",
            help="name of a signal header in input data [optional]")
        common_group.add_argument("-annotation_label", "--annotation_label",
            help="name of a annotation header in input data [optional]")
        common_group.add_argument("-time_label", "--time_label",
            help="name of a time header in input data [optional]")
        common_group.add_argument("-time_format", "--time_format",
            help="""time format, for example, for '08:21:44.020' use %H:%M:%S.%f""") # @IgnorePep8
        common_group.add_argument("-headers_count", "--headers_count",
            help="""number of headers lines in data source (program tries to determine this values on it's own)""", # @IgnorePep8
            type=int, default=0)
        common_group.add_argument("-separator", "--separator",
            help="a separator used between columns, one from the set: " + getSeparatorLabels() + ", <custom>; note: the application tries to discover a separator on its own") # @IgnorePep8
        common_group.add_argument("-dav", "--display_annotation_values",
            help="""display unique annotations values presented in data source files""", # @IgnorePep8
            type=to_bool, default=False)
        common_group.add_argument("-filters_names", "--filters_names",
            help="""use filters; available filters: """ + commas(get_filters_short_names())) # @IgnorePep8
        common_group.add_argument("-ea", "--excluded_annotations",
            help="""specifies which values (separated by a comma) have to be interpreted as true annotations values; if not specified then all non-0 values in a annotation column are such entities""")  # @IgnorePep8
        common_group.add_argument("-ordinal", "--ordinal_column_name",
            help="""name of the ordinal column, index or time it depends on window size unit, which will be the first column in outcomes""")  # @IgnorePep8
        common_group.add_argument("-use_identity_line", "--use_identity_line",
            help="during calculations use identity line",
            type=to_bool, default=True)
        common_group.add_argument("-use_buffer", "--use_buffer",
            help="use buffer during statistics calculations",
            type=to_bool, default=True)
        common_group.add_argument("-override_existing_outcomes", "--override_existing_outcomes", # @IgnorePep8
            help="override existing outcomes",
            type=to_bool, default=False)
        common_group.add_argument("-sample_step", "--sample_step",
            help="""how big have to be a step for window resampling size; it is assumed that this quantity is expressed in signal unit value 0 means no use of window resampling size at all [optional]""", # @IgnorePep8
            type=int)
        common_group.add_argument("-stepper", "--stepper",
            help="""to define amount by which data window have to jump during process of data expressed in number of data items or in time units by suffix: s - second, m - minute, h - hour; examples: 100, 5m [optional]""") # @IgnorePep8
        common_group.add_argument("-output_prefix", "--output_prefix",
            help="""a label included in a name of an output file [optional]""")
        common_group.add_argument("-save_parameters", "--save_parameters",
            help="""save parameters of poincare plot generation""",
            type=to_bool, default=True)
        common_group.add_argument("-progress_mark", "--progress_mark",
            help="""show progress bar during generation of statistics""",
            type=to_bool, default=True)
        common_group.add_argument("-print_first_signal", "--print_first_signal",
            help="""print the first row of a signal""",
            type=to_bool, default=True)
        common_group.add_argument("-shuffle_data", "--shuffle_data",
            help="""shuffle data""",
            type=to_bool, default=False)

        statistics_group = parser.add_argument_group(
                            title=STATISTICS_PARAMETERS_GROUP,
                            description="Statistics parameters")
        statistics_group.add_argument("-out_prec", "--output_precision",
            help="precision for output data",
            default="10,5")
        statistics_group.add_argument("-statistics_names", "--statistics_names", # @IgnorePep8
            help="list of statistics names to calculate, available: " + commas(get_statistics_names(ALL_STATISTICS))) # @IgnorePep8
        statistics_group.add_argument("-summary_statistics_names", "--summary_statistics_names", # @IgnorePep8
            help="list of summary statistics names to calculate, available: " + commas(get_summary_statistics_names(ALL_SUMMARY_STATISTICS))) # @IgnorePep8
        statistics_group.add_argument("-output_separator", "--output_separator", # @IgnorePep8
            help="a separator for output data",
            default=",")
        statistics_group.add_argument("-add_headers", "--add_headers",
            help="headers in the output files",
            type=to_bool, default=True)
        statistics_group.add_argument("-group_data_filename", "--group_data_filename", # @IgnorePep8
            help="""used as a file where are stored all input files according to data_dir and extension and this overall file is used as a input file for further analisys [optional]""") # @IgnorePep8
        statistics_group.add_argument("-headers_aliases", "--headers_aliases",
            help="""aliases for output headers, this parameter must correspond to items of statistics_names""")  # @IgnorePep8
        statistics_group.add_argument("-summary_headers_aliases", "--summary_headers_aliases", # @IgnorePep8
            help="""aliases for output summary headers, this parameter must correspond to items of summary_statistics_names""")  # @IgnorePep8
        statistics_group.add_argument("-dynamic_plots_headers", "--dynamic_plots_headers", # @IgnorePep8
            help="""draw many plots base on data from _source_file and collection of headers grouped by a semicolon, elements in a group are separated by a comma""")  # @IgnorePep8
        statistics_group.add_argument("-timing", "--timing",
            help="add timing column",
            type=to_bool, default=False)

        movie_group = parser.add_argument_group(
                            title=MOVIE_PARAMETERS_GROUP,
                            description="Movie parameters")
        movie_group.add_argument("-movie_name", "--movie_name",
            help="""name of a movie for Poincare plot evolutions""")
        movie_group.add_argument("-movie_dir", "--movie_dir",
            help="""directory for movie files, if is not present assumed output_dir""") # @IgnorePep8
        movie_group.add_argument("-movie_multiprocessing_factor", "--movie_multiprocessing_factor", # @IgnorePep8
            help="""to generate a poincare plot movie use multiprocessing, active on multiprocessing hardware, greater value > 0 give use a few processors""",  # @IgnorePep8
            type=int)
        movie_group.add_argument("-movie_bin_size", "--movie_bin_size",
            help="""movie bin size """, type=int, default=500)
        movie_group.add_argument("-movie_fps", "--movie_fps",
            help="""a movie fps [optional]""", type=int, default=700)
        movie_group.add_argument("-movie_save_partial", "--movie_save_partial",
            help="""save partial generated movie""",
            type=to_bool, default=True)
        movie_group.add_argument("-movie_not_save", "--movie_not_save",
            help="""not save a movie, used to save only frames""",
            type=to_bool, default=False)
        movie_group.add_argument("-movie_skip_to_frame", "--movie_skip_to_frame", # @IgnorePep8
            help="""skip to a movie frame [optional]""", type=int, default=0)
        movie_group.add_argument("-movie_experimental_code", "--movie_experimental_code", # @IgnorePep8
            help="""use some movie experimental code only for tests""",
            type=to_bool, default=False)
        movie_group.add_argument("-movie_animated", "--movie_animated",
            help="""use animation API to generate a movie; required mencoder and ffmpeg""", # @IgnorePep8
            type=to_bool, default=False)
        movie_group.add_argument("-movie_calculate_all_frames", "--movie_calculate_all_frames", # @IgnorePep8
            help="""before generation png files all frames are calculated""",
            type=to_bool, default=True)
        movie_group.add_argument("-movie_standard_generation", "--movie_standard_generation", # @IgnorePep8
            help="""standard generation of movie by use of matplotlib plotting library [could be very slow for huge recordings (e.g. 24h)]""", # @IgnorePep8
            type=to_bool, default=False)
        movie_group.add_argument("-movie_dpi", "--movie_dpi",
            help="""movie dpi""", default=70, type=int)
        movie_group.add_argument("-movie_width", "--movie_width",
            help="""movie width""",
            default=550, type=int)
        movie_group.add_argument("-movie_height", "--movie_height",
            help="""movie height""",
            default=550, type=int)
        movie_group.add_argument("-movie_active_size", "--movie_active_size",
            help="""movie active plot data point size""",
            default=3, type=int)
        movie_group.add_argument("-movie_inactive_size", "--movie_inactive_size", # @IgnorePep8
            help="""movie inactive plot data point size""",
            default=3, type=int)
        movie_group.add_argument("-movie_centroid_size", "--movie_centroid_size", # @IgnorePep8
            help="""movie centroid plot data point size""",
            default=6, type=int)
        movie_group.add_argument("-movie_prefixed_by_source", "--movie_prefixed_by_source", # @IgnorePep8
            help="""all intermediate frame files and output movie filename is prefixed by a name of a source file (minus extension)""", # @IgnorePep8
            type=to_bool, default=True)
        movie_group.add_argument("-movie_clean_frames", "--movie_clean_frames",
            help="""after movie creation all frame files are deleted""",
            type=to_bool, default=True)
        movie_group.add_argument("-x_label", "--x_label",
            help="""label of X axis of poincare plot [optional]""")
        movie_group.add_argument("-y_label", "--y_label",
            help="""label of Y axis of poincare plot [optional]""")
        movie_group.add_argument("-movie_title", "--movie_title",
            help="""movie title [optional]""")
        movie_group.add_argument("-movie_frame_step", "--movie_frame_step",
            help="""only every movie step a frame is generated""",
            default=-1, type=int)
        movie_group.add_argument("-movie_identity_line", "--movie_identity_line",
            help="""draw identity line in Poincare plot """,
            type=to_bool, default=False)
        movie_group.add_argument("-movie_hour_label", "--movie_hour_label",
            help="""label of hour in a Poincare plot [optional]""")
        movie_group.add_argument("-movie_minute_label", "--movie_minute_label",
            help="""label of minute in a Poincare plot [optional]""")
        movie_group.add_argument("-movie_second_label", "--movie_second_label",
            help="""label of second in a Poincare plot [optional]""")
        movie_group.add_argument("-movie_time_label_in_line", "--movie_time_label_in_line",
            help="""draw time label (hour, minute, second) in one line at a Poincare plot [optional]""",
            type=to_bool, default=False)
        movie_group.add_argument("-movie_time_label_font_size", "--movie_time_label_font_size",
            help="""movie time label font size [optional]""",
            default=-1, type=int)
        movie_group.add_argument("-movie_time_label_prefix", "--movie_time_label_prefix",
            help="""movie time label prefix [optional]""",
            default=None)
        movie_group.add_argument("-movie_title_font_size", "--movie_title_font_size",
            help="""movie title font size [optional]""",
            default=-1, type=int)
        movie_group.add_argument("-movie_axis_font_size", "--movie_axis_font_size",
            help="""movie axis font size [optional]""",
            default=-1, type=int)
        movie_group.add_argument("-movie_axis_font", "--movie_axis_font",
            help="""movie axis font, example: '15 pt bold italic' [optional]""",
            default=None)
        movie_group.add_argument("-movie_title_font", "--movie_title_font",
            help="""movie title font, example: '15 pt bold italic' [optional]""",
            default=None)
        movie_group.add_argument("-movie_tick_font", "--movie_tick_font",
            help="""movie tick font, example: '15 pt bold italic' [optional]""",
            default=None)
        movie_group.add_argument("-movie_frame_pad", "--movie_frame_pad",
            help="""movie frame pad, the space used for axes and ticks labels [optional]""",
            default=-1, type=int)
        movie_group.add_argument("-movie_create_time_label", "--movie_create_time_label",
            help="""does it create time label ? (default=True)[optional]""",
            type=to_bool, default=True)
        movie_group.add_argument("-movie_frame_filename_with_time", "--movie_frame_filename_with_time",
            help="""movie frame filename includes timestamp (default=False)[optional]""",
            type=to_bool, default=False)

        #add information about parameters
        for group in parser._action_groups:
            if not group.description == None:
                for action in group._group_actions:
                    self.__p__.addParameterInfo(
                                        group=group.title,
                                        name=action.dest,
                                        default=action.default,
                                        _help=action.help,
                                        group_description=group.description)
        return parser


if __name__ == '__main__':

    ppManager = PoincarePlotManager()
    __args = ppManager.getParser().parse_args()
    #copy all parameters from __args object into ppManager object
    copy_object(__args, ppManager)
    ppManager.movie_dir = nvl(__args.movie_dir, ppManager.output_dir)

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
