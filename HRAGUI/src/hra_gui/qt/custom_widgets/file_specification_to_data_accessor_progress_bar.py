'''
Created on 7 maj 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from hra_math.model.data_vector_accessor import get_data_accessor_from_file_specification # @IgnorePep8
    from hra_gui.qt.custom_widgets.progress_bar import ProgressDialogManager
except ImportError as error:
    ImportErrorMessage(error, __name__)


class FileSpecificationToDataAccessorProgressBar(object):
    """
    progress bar to create data accessor objects based on
    file specification objects, this widget is especially
    suitable in situation of huge collection of file specification objects
    """
    def __init__(self, _parent, _files_specifications):
        self.__files_specifications__ = _files_specifications
        self.__parent__ = _parent
        self.__data_accessors__ = []

    def start(self):
        self.__data_accessors__ = []
        count = len(self.__files_specifications__)
        progressManager = ProgressDialogManager(self.__parent__,
                                                label_text=("Preparing data"),
                                                max_value=count)
        with progressManager as progress:
            for idx in range(count):
                if (progress.wasCanceled()):
                    break
                progress.increaseCounter()
                self.__data_accessors__.append(
                        get_data_accessor_from_file_specification(
                                        self.__parent__,
                                        self.__files_specifications__[idx]))

    @property
    def data_accessors(self):
        return self.__data_accessors__
