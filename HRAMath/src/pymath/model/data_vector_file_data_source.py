'''
Created on 24 kwi 2013

@author: jurek
'''
from pymath.model.numerical_file_data_source import NumericalFileDataSource
try:
    import collections
    from pycore.collections_utils import nvl
    from pycore.misc import Params
    from pymath.utils.utils import print_import_error
    from pymath.model.data_vector import DataVector
    from pymath.model.utils import get_unique_annotations
except ImportError as error:
    print_import_error(__name__, error)

__Entities__ = collections.namedtuple('__Entities__',
                                      ['signal', 'annotation', 'time'])


class DataVectorFileDataSource(NumericalFileDataSource):
    """
    class to load numerical data file into data vector
    """

    def __init__(self, **params):
        super(DataVectorFileDataSource, self).__init__(**params)
        self.params = Params(**params)
        self.__indexes__ = __Entities__(nvl(self.params.signal_index, -1),
                                       nvl(self.params.annotation_index, -1),
                                       nvl(self.params.time_index, -1))
        self.__headers__ = None
        self.__data_vector__ = None

    @property
    def headers(self):
        if self.__headers__ == None:
            headers = super(DataVectorFileDataSource, self).headers
            vector_headers = [(None if col == -1 else headers[col])
                                        for col in self.__indexes__]
            self.__headers__ = __Entities__(*vector_headers)

        return [header for header in self.__headers__ if not header == None]

    @property
    def headers_with_col_index(self):
        return [list(enumerate(header)) for header in self.headers]

    def getDataVector(self):
        if self.__data_vector__ == None:
            _data = self.getData()

            (signal, annotation, time) = \
                  [(None if index == -1 else _data[index:index + 1][0])
                    for index in self.__indexes__]

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
            self.__data_vector__.filename = self.__file__
        return self.__data_vector__

    def getUniqueAnnotations(self):
        return get_unique_annotations(self.getData().annotation)
