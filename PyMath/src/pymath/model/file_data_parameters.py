'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from pycore.collections_utils import nvl
except ImportError as error:
    print_import_error(__name__, error)


class FileDataParameters(object):
    """
    parameters concering file data source
    """
    def __init__(self):
        self.__extension__ = '*'

    @property
    def data_dir(self):
        """
        [obligatory if data_file is NOT specified]
        directory where input data files are located
        """
        return self.__data_dir__

    @data_dir.setter
    def data_dir(self, _data_dir):
        self.__data_dir__ = _data_dir

    @property
    def extension(self):
        """
        [obligatory if data_dir is specified]
        extension of data input files in the form '*.ext'
        example: *.rea
        """
        return self.__extension__

    @extension.setter
    def extension(self, _extension):
        self.__extension__ = _extension

    @property
    def output_dir(self):
        """
        [obligatory]
        a directory for outcomes files
        """
        return self.__output_dir__

    @output_dir.setter
    def output_dir(self, _output_dir):
        self.__output_dir__ = _output_dir

    @property
    def data_file(self):
        """
        [obligatory if data_dir is NOT specified]
        this is an alternative option to set up one file
        (with full path) as data source
        """
        return self.__data_file__

    @data_file.setter
    def data_file(self, _data_file):
        self.__data_file__ = _data_file

    @property
    def output_precision(self):
        """
        [optional]
        precision for output data [default: 10,5]
        """
        return '10,5' if self.__output_precision__ == None \
                else self.__output_precision__

    @output_precision.setter
    def output_precision(self, _output_precision):
        self.__output_precision__ = _output_precision

    @property
    def output_separator(self):
        """
        [optional]
        output separator between data columns
        default: ',' (comma)
        """
        return self.__output_separator__

    @output_separator.setter
    def output_separator(self, _output_separator):
        self.__output_separator__ = _output_separator

    @property
    def output_headers(self):
        """
        [optional]
        headers in the output files
        default: True
        """
        return self.__output_headers__

    @output_headers.setter
    def output_headers(self, _output_headers):
        self.__output_headers__ = _output_headers

    @property
    def separator(self):
        """
        [optional]
        a separator used between input data columns;
        to get list of standard separators call a function:
        getSeparatorLabels()
        [module: pymath.time_domain.poincare_plot.poincare_plot]
        note: the application tries to discover a separator itself
        """
        return self.__separator__

    @separator.setter
    def separator(self, _separator):
        self.__separator__ = _separator

    @property
    def skip_existing_outcomes(self):
        """
        [optional]
        skip processing data file for existing outcomes
        default: False
        """
        return nvl(self.__skip_existing_outcomes__, False)

    @skip_existing_outcomes.setter
    def skip_existing_outcomes(self, _skip_existing_outcomes):
        self.__skip_existing_outcomes__ = _skip_existing_outcomes

    def setProperties(self, _object):
        """
        method which set up some parameters from this object into
        another object, it is some kind of 'copy constructor'
        """
        setattr(_object, 'skip_existing_outcomes', self.skip_existing_outcomes)
        setattr(_object, 'output_dir', self.output_dir)
        setattr(_object, 'output_precision', self.output_precision)
        setattr(_object, 'output_separator', self.output_separator)
        setattr(_object, 'output_headers', self.output_headers)
