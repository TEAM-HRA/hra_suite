'''
Created on 7 maj 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from hra_math.model.data_vector_accessor import get_data_accessor_from_file_specification # @IgnorePep8
    from hra_math.model.data_vectors_accessors_group import DataVectorsAccessorGroup # @IgnorePep8
    from hra_gui.qt.custom_widgets.progress_bar import ProgressDialogManager
except ImportError as error:
    ImportErrorMessage(error, __name__)


class FilesSpecificationsToDataAccessorsGroupConverter(object):
    """
    converter to create data accessor objects based on files specification
    objects, data accessor objects are put into DataVectorsAccessorGroup
    object; this widget is especially suitable in situation of huge collection
    of file specification objects because of use a progress bar widget
    """
    def __init__(self, _parent, _files_specifications):
        self.__data_vectors_accessor_group__ = DataVectorsAccessorGroup()
        count = len(_files_specifications)
        progressManager = ProgressDialogManager(_parent,
                                                label_text=("Preparing data"),
                                                max_value=count)
        with progressManager as progress:
            for idx in range(count):
                if (progress.wasCanceled()):
                    break
                progress.increaseCounter()
                vector_accessor = get_data_accessor_from_file_specification(
                                        _parent, _files_specifications[idx])
                self.__data_vectors_accessor_group__.addDataVectorAccessor(
                                                            vector_accessor)

    @property
    def data_vectors_accessors_group(self):
        return self.__data_vectors_accessor_group__
