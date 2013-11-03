'''
Created on 29 maj 2013

@author: jurek
'''
from hra_math.utils.utils import print_import_error
try:
    import pylab as pl
    from hra_core.misc import Params
    from hra_core.io_utils import FileSource
except ImportError as error:
    print_import_error(__name__, error)


class NumericalFileDataSource(FileSource):
    """
    class to load numerical data file
    """

    def __init__(self, **params):
        super(NumericalFileDataSource, self).__init__(**params)
        self.params = Params(**params)

    @FileSource.file_decorator
    def getData(self):
        # check if a separator is a white space
        if not self.params.separator == None and \
            len(self.params.separator.strip()) == 0:
            return pl.loadtxt(self._file,
                              skiprows=self.headers_count,
                              unpack=True)
        else:
            return pl.loadtxt(self._file,
                              skiprows=self.headers_count,
                              unpack=True,
                              delimiter=self.params.separator)
