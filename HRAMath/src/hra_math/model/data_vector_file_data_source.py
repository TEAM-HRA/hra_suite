'''
Created on 24 kwi 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import collections
    import pylab as pl
    from hra_core.collections_utils import nvl
    from hra_core.misc import Params
    from hra_math.model.data_vector import DataVector
    from hra_math.model.utils import get_unique_annotations
    from hra_math.model.numerical_file_data_source \
            import NumericalFileDataSource
    from hra_math.model.text_file_data_source import TextFileDataSource
except ImportError as error:
    print_import_error(__name__, error)

__Entities__ = collections.namedtuple('__Entities__',
                                      ['signal', 'annotation', 'time'])


class DataVectorFileDataSource(object):
    """
    class to load numerical data file into data vector
    """

    def __init__(self, **params):
        self.params = Params(**params)
        self.__indexes__ = __Entities__(nvl(self.params.signal_index, -1),
                                       nvl(self.params.annotation_index, -1),
                                       nvl(self.params.time_index, -1))
        self.__headers__ = None
        self.__data_vector__ = None
        if self.params.time_index == None:
            self.__data_source__ = NumericalFileDataSource(**params)
        else:
            #if there is separate column of time all data are loaded
            #in string format, getDataVector method do further processing
            #and change into numerical values
            self.__data_source__ = TextFileDataSource(**params)

    @property
    def headers(self):
        if self.__headers__ == None:
            headers = self.__data_source__.headers_first_line
            vector_headers = [(None if col == -1 else headers[col])
                                        for col in self.__indexes__]
            self.__headers__ = __Entities__(*vector_headers)

        return [header for header in self.__headers__ if not header == None]

    @property
    def headers_with_col_index(self):
        return [list(enumerate(header))
                                for header in self.__data_source__.headers]

    def getDataVector(self):
        if self.__data_vector__ == None:
            _data = self.__data_source__.getData()

            (signal, annotation, time) = \
                  [(None if index == -1 else _data[index:index + 1][0])
                    for index in self.__indexes__]

            #if elements of data source are strings they are converted to float
            if isinstance(self.__data_source__, TextFileDataSource):
                (signal, annotation, time) = \
                    self.__convertToFloats__(signal, annotation, time)

            if annotation == None and not signal == None:
                annotation = 0 * signal
            if not annotation == None:
                annotation = annotation.astype(int)

            self.headers  # to generate headers if not present yet

            self.__data_vector__ = DataVector(
                                signal=signal,
                                annotation=annotation,
                                time=time,
                                signal_header=self.__headers__.signal,
                                annotation_header=self.__headers__.annotation,
                                time_header=self.__headers__.time)
            # set up an additional property
            self.__data_vector__.filename = self.__data_source__._file
        return self.__data_vector__

    def getUniqueAnnotations(self):
        return get_unique_annotations(self.getData().annotation)

    def __convertToFloats__(self, signal, annotation, time):
        """
        method converts all string values in signal, annotation arrays
        into float values;
        here is one assumption: time array is in float format already
        """
        floats = pl.ones(len(signal))
        if annotation == None:
            entities = zip(signal)
        else:
            entities = zip(signal, annotation)
        for idx, values in enumerate(entities):
            for value in values:
                try:
                    pl.float64(value)  # check if it can be converted to float
                except ValueError:
                    floats[idx] = 0  # the value is NOT like float type
                    break

        true_floats = pl.nonzero(floats)  # get indexes of non-zero positions
        signal = signal[true_floats].astype(float)
        if not annotation == None:
            annotation = annotation[true_floats].astype(float)
        if not time == None:
            time = time[true_floats]

        return signal, annotation, time
