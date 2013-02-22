'''
Created on 27-07-2012

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    import os
    import argparse
    import glob
    import numpy as np
    from pycore.misc import Separator
    from pycore.misc import extract_number
    from pycore.misc import extract_alphabetic
    from pycore.units import get_time_unit
    from pymath.utils.array_utils import \
        get_max_index_for_cumulative_sum_greater_then_value
    from pymath.utils.io_utils import NumpyCSVFile
    from pymath.statistics.statistics import StatisticsFactory
    from pymath.statistics.statistics import Statistic
    from pymath.statistics.statistics import SD1Statistic
    from pymath.statistics.statistics import SD2Statistic
    from pymath.statistics.statistics import SsStatistic
    from pymath.statistics.statistics import SD21Statistic
    from pymath.statistics.statistics import RStatistic
    from pymath.statistics.statistics import RMSSDStatistic
    from pymath.statistics.statistics import SD1upStatistic
    from pymath.statistics.statistics import SD1downStatistic
    from pymath.statistics.statistics import NupStatistic
    from pymath.statistics.statistics import NdownStatistic
    from pymath.statistics.statistics import NonStatistic
    from pymath.statistics.statistics import SymmetryStatistic
    from pymath.datasources import DataVector
    from pymath.datasources import FileDataSource
    from pymath.interpolation import Interpolation
    from pymath.time_domain.poincare_plot.filters import FilterManager
    #from pymath.time_domain.poincare_plot.filters import Filter
    from pymath.time_domain.poincare_plot.filters import DataVectorFilter
    from pycore.collections_utils import commas
    #from pycore.collections_utils import get_as_list
    #from pymath.frequency_domain.fourier import FourierTransformManager
    #from pymath.frequency_domain.fourier import FastFourierTransform
except ImportError as error:
    print_import_error(__name__, error)


DEFAULT_OUTCOME_DIRECTORY = os.path.join(os.getcwd(), 'pp_outcomes')


def getDefaultStatisticsNames():
    return commas(Statistic.getSubclassesShortNames())


def getFiltersNames():
    return commas(DataVectorFilter.getSubclassesShortNames())


def getInterpolationNames():
    return commas(Interpolation.getSubclassesShortNames())


class PoincarePlotManager(object):
    def __init__(self):
        self.__data_dir__ = os.getcwd()
        self.__extension__ = '*'
        self.__window_shift__ = 1
        self.__filter_manager__ = FilterManager()

    # if parameter is not set in the __init__() this method then returns None
    def __getattr__(self, name):
        return None

    @property
    def data_dir(self):
        return self.__data_dir__

    @data_dir.setter
    def data_dir(self, _data_dir):
        self.__data_dir__ = _data_dir

    @property
    def extension(self):
        return self.__extension__

    @extension.setter
    def extension(self, _extension):
        self.__extension__ = _extension

    @property
    def window_size(self):
        return self.__window_size__

    @window_size.setter
    def window_size(self, _window_size):
        self.__window_size__ = extract_number(_window_size, convert=int)
        self.__window_size_unit__ = extract_alphabetic(_window_size,
                                                       convert=str.lower)

    @property
    def window_size_unit(self):
        return self.__window_size_unit__

    @property
    def output_dir(self):
        return self.__output_dir__

    @output_dir.setter
    def output_dir(self, _output_dir):
        self.__output_dir__ = _output_dir

    @property
    def statistics_names(self):
        return self.__statistics_names__

    @statistics_names.setter
    def statistics_names(self, _statistics_names):
        self.__statistics_names__ = _statistics_names

    @property
    def headers(self):
        return self.__headers__

    @headers.setter
    def headers(self, _headers):
        self.__headers__ = _headers

    @property
    def signal_index(self):
        return self.__signal_index__

    @signal_index.setter
    def signal_index(self, _signal_index):
        self.__signal_index__ = _signal_index

    @property
    def annotation_index(self):
        return self.__annotation_index__

    @annotation_index.setter
    def annotation_index(self, _annotation_index):
        self.__annotation_index__ = _annotation_index

    @property
    def time_index(self):
        return self.__time_index__

    @time_index.setter
    def time_index(self, _time_index):
        self.__time_index__ = _time_index

    @property
    def separator(self):
        return self.__separator__

    @separator.setter
    def separator(self, _separator):
        self.__separator__ = _separator

    @property
    def data_file(self):
        return self.__data_file__

    @data_file.setter
    def data_file(self, _data_file):
        self.__data_file__ = _data_file

    @property
    def window_shift(self):
        return self.__window_shift__

    @window_shift.setter
    def window_shift(self, _window_shift):
        self.__window_shift__ = _window_shift
        self.__filter_manager__.shift = _window_shift

    @property
    def output_precision(self):
        return self.__output_precision__

    @output_precision.setter
    def output_precision(self, _output_precision):
        self.__output_precision__ = _output_precision

    @property
    def use_filters(self):
        return self.__use_filters__

    @use_filters.setter
    def use_filters(self, _filters_names):
        self.__filter_manager__.addFiltersByNames(_filters_names)

    def addFilter(self, name_or_object, _excluded_annotations=None):
        self.__filter_manager__.addFilter(name_or_object,
                                          _excluded_annotations)

    @property
    def use_fft_interpolation(self):
        return self.__use_fft_interpolation__

    @use_fft_interpolation.setter
    def use_fft_interpolation(self, _use_fft_interpolation):
        self.__use_fft_interpolation__ = _use_fft_interpolation

    def generate(self):
        """
        the method which starts to generate Poincare Plot parameters
        """
        self.__process__(self.__process_file__)

    def __process__(self, _file_handler, disp=True, **params):
        """
        the method which starts to generate Poincare Plot parameters
        """

        sign_multiplicator = 80
        file_counter = 0
        if self.data_file:  # data_file parameter is superior to data_dir parameter @IgnorePep8
            if os.path.exists(self.data_file) == False:
                if disp:
                    print('The file: ' + self.data_file + " doesn't exist")
            else:
                file_counter = 1
                if disp:
                    print('Processing file: ' + self.data_file)
                _file_handler(self.data_file, **params)
        else:
            path = self.data_dir + ('*.*'
                            if self.extension == None else self.extension)
            for _file in glob.glob(path):
                if os.path.isfile(_file):
                    file_counter = file_counter + 1
                    if disp:
                        print('=' * sign_multiplicator)
                        print('Processing file: ' + _file)
                    _file_handler(_file, **params)
        if disp:
            for _ in range(3):
                print('*' * sign_multiplicator)
            print('Processing finished')
            if file_counter == 0:
                print('No files to process [' + self.data_dir
                                            + self.extension + ']')
            else:
                print('Number of processed files: ' + str(file_counter))

    def __process_file__(self, _file):
        file_data_source = FileDataSource(_file=_file,
                               signal_index=self.signal_index,
                               annotation_index=self.annotation_index,
                               time_index=self.time_index)
        data = file_data_source.getData()
        parameters = {}
#        if self.__use_fft_interpolation__:
#            fourierManager = FourierTransformManager(FastFourierTransform,
#                                    self.__use_fft_interpolation__)
#            parameters.update(fourierManager.calculate(data))
        with NumpyCSVFile(output_dir=self.output_dir,
                         reference_filename=_file,
                         output_precision=self.output_precision) as csv:
            statisticsFactory = StatisticsFactory(self.statistics_names,
                            statistics_handlers=self.__statistics_handlers__)
            for data_segment in PoincarePlotSegmenter(data,
                                    self.window_size,
                                    shift=self.window_shift,
                                    window_size_unit=self.window_size_unit):
                data_segment = self.__filter_manager__.filter(data_segment)
                statistics = statisticsFactory.statistics(data_segment)
                parameters.update(statistics)
                csv.write(parameters)
                #print(str(statistics))

    def addStatisticHandler(self, _handler=None):
        if self.__statistics_handlers__ == None:
            self.__statistics_handlers__ = []
        self.__statistics_handlers__.append(_handler)

    def getUniqueAnnotations(self):
        unique_annotations = []
        self.__process__(self.__process_annotations__, disp=False,
                         _unique_annotations=unique_annotations)
        return set(unique_annotations)

    def __process_annotations__(self, _file, _unique_annotations=None):
        file_data_source = FileDataSource(_file=_file,
                                annotation_index=self.annotation_index)
        _unique_annotations[len(_unique_annotations):] = \
                    file_data_source.getUniqueAnnotations()


class PoincarePlot(StatisticsFactory):
    '''
    classdocs
    '''

    def __init__(self, data_source=None):
        statistics_classes = (
                            # MeanStatistic,
                            # SDStatistic,
                            # SDRRStatistic,
                            # NtotStatistic,
                            SD1Statistic,
                            SD2Statistic,
                            SsStatistic,
                            SD21Statistic,
                            RStatistic,
                            RMSSDStatistic,
                            SD1upStatistic,
                            SD1downStatistic,
                            NupStatistic,
                            NdownStatistic,
                            NonStatistic,
                            SymmetryStatistic)
        StatisticsFactory.__init__(self, statistics_classes,
                                   data_source=data_source)

    def __rrshift__(self, other):
        if (isinstance(other, DataVector)):
            self.signal = other.signal
            self.annotation = other.annotation
            return self.statistics

#    @staticmethod
#    def poincareOld(__signal__, annotation, filtering):
#        if filtering == 1:
#            filtered_signal = Filter.filter(__signal__, annotation)
#            x_p, x_pp = Filter.pfilter(__signal__, annotation)
#        else:
#            x_p = __signal__[arange(0, len(__signal__) - 1)]
#            x_pp = __signal__[arange(1, len(__signal__))]
#            filtered_signal = __signal__
#
#        RR_mean = Statistics.Mean(filtered_signal)
#        sdrr = Statistics.SDRR(filtered_signal)
#        rmssd = Statistics.RMSSD(x_p, x_pp)
#        sd1 = Statistics.SD1(x_p, x_pp)
#        sd2 = Statistics.SD2(x_p, x_pp)
#        sd21 = Statistics.SD21(x_p, x_pp)
#        s = Statistics.Ss(x_p, x_pp)
#        r = Statistics.R(x_p, x_pp)
#        sd1up = Statistics.SD1up(x_p, x_pp)
#        sd1down = Statistics.SD1down(x_p, x_pp)
#        nup = Statistics.Nup(x_p, x_pp)
#        ndown = Statistics.Ndown(x_p, x_pp)
#        non = Statistics.Non(x_p, x_pp)
#        ntot = Statistics.N_tot(filtered_signal)
#        tot_time = sum(filtered_signal) / (1000 * 60)
#        asym = 0
#        if sd1up > sd1down:
#            asym = 1
#        return RR_mean, sdrr, rmssd, sd1, sd2, sd21, s, r, sd1up, sd1down,
#            asym, nup, ndown, non, ntot, tot_time


class PoincarePlotSegmenter(object):

    def __init__(self, data, window_size,  shift=1, window_size_unit=None):
        self.__data__ = data
        self.__window_size__ = window_size
        self.__shift__ = shift
        self.__index__ = 0
        self.__window_size_unit__ = window_size_unit

        #this means a user put window size in some unit
        if self.__window_size_unit__:

            #get time unit of window size
            unit = get_time_unit(self.__window_size_unit__)

            #convert signal unit into window size unit,
            #for example express milliseconds in minutes
            multiplier = unit.expressInUnit(self.__data__.signal_unit)

            #express window size in units of a signal
            self.__window_size__ = multiplier * window_size
        else:
            if self.__window_size__ > len(self.__data__.signal):
                raise Exception('Poincare window size greater then signal size !!!') #@IgnorePep8

    def __iter__(self):
        return self

    def next(self):
        #this means a user expresses window size in a unit
        if self.__window_size_unit__:
            max_index = get_max_index_for_cumulative_sum_greater_then_value(
                                                self.__data__.signal,
                                                self.__window_size__,
                                                self.__index__)
            if max_index == -1:
                raise StopIteration

            #new window size is a difference between max_index a start index
            signal_size = max_index - self.__index__
        else:
            signal_size = self.__window_size__
        if self.__index__ + signal_size + self.__shift__ <= len(self.__data__.signal): # @IgnorePep8
            indexes = np.arange(self.__index__, self.__index__ + signal_size)
            signal = self.__data__.signal.take(indexes)

            indexes_plus = np.arange(self.__index__,
                                 self.__index__ + signal_size - self.__shift__)
            signal_plus = self.__data__.signal.take(indexes_plus)

            indexes_minus = np.arange(self.__index__ + self.__shift__,
                                  self.__index__ + signal_size)
            signal_minus = self.__data__.signal.take(indexes_minus)

            annotation = (None if self.__data__.annotation == None else
                          self.__data__.annotation.take(indexes))

            self.__index__ += self.__shift__

            return DataVector(signal=signal,
                              signal_plus=signal_plus,
                              signal_minus=signal_minus,
                              annotation=annotation,
                              signal_unit=self.__data__.signal_unit)
        else:
            raise StopIteration


#an example of statistic handler
#def stat_double(signal_plus, signal_minus):
#    print('stat double: ' + str(signal_plus.sum() * 2))
#    return signal_plus.sum() * 2


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
                in time units by suffix: s - second, m - minute, h - hour""")
    parser.add_argument("-ws", "--window_shift", type=int,
                help="window data shift between two sets of signals",
                default=1)
    parser.add_argument("-o", "--output_dir",
                help="directory for outcomes [default: " +
                        DEFAULT_OUTCOME_DIRECTORY + "]",
                default=DEFAULT_OUTCOME_DIRECTORY)
    parser.add_argument("-out_prec", "--output_precision",
                help="precision for output data [default: 10,5]",
                default="10,5")
    parser.add_argument("-s", "--statistics_names",
                help="list of statistics names to calculate, defaults to: " +
                        getDefaultStatisticsNames(),
                default=getDefaultStatisticsNames())
    #parser.add_argument("-r", "--headers",
    #            help="display lines of headers (not implemented yet)",
    #            default="")
    parser.add_argument("-si", "--signal_index", type=int,
                help="index of a signal column", default=-1)
    parser.add_argument("-ai", "--annotation_index", type=int,
                help="index of an annotation column", default=-1)
    parser.add_argument("-ti", "--time_index", type=int,
                help="index of a time column", default=-1)
    parser.add_argument("-p", "--separator",
                help="a separator used between columns, one from the set: " +
                     ", ".join(Separator.getSeparatorsLabels()) + ", <custom>")
    parser.add_argument("-dav", "--display_annotation_values",
                help="display unique annotations values [True|False]",
                type=to_bool, default=False)
    parser.add_argument("-df", "--display_filters",
                help="display list of available filters [True|False]",
                type=to_bool, default=False)
    parser.add_argument("-uf", "--use_filters",
                help="""use filters in a form: <filter_name>[<annotations
                    values separated by '-']; available filters: """
                    + getFiltersNames())
    parser.add_argument("-ff", "--use_fft_interpolation",
                help="""use Fast Fourier Transform with interpolation: """ +
                        getInterpolationNames())
    __args = parser.parse_args()

    ppManager = PoincarePlotManager()
    ppManager.data_file = __args.data_file
    ppManager.data_dir = __args.data_dir
    ppManager.extension = __args.extension
    ppManager.window_size = __args.window_size
    ppManager.window_shift = __args.window_shift
    ppManager.output_dir = __args.output_dir
    ppManager.statistics_names = __args.statistics_names
    ppManager.signal_index = __args.signal_index
    ppManager.annotation_index = __args.annotation_index
    ppManager.time_index = __args.time_index
    ppManager.output_precision = __args.output_precision
    ppManager.use_filters = __args.use_filters
    ppManager.use_fft_interpolation = __args.use_fft_interpolation
    _disp = False
    #ppManager.addStatisticHandler(stat_double)
    if __args.display_annotation_values == True:
        _disp = True
        print('Annotations: ' + commas(ppManager.getUniqueAnnotations(),
                                       _default='none'))
    if __args.display_filters == True:
        _disp = True
        print('Filters: ' + getFiltersNames())
    if _disp == False:
        ppManager.generate()
