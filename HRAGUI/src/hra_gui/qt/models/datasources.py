'''
Created on 02-01-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_core.collections_utils import empty_string
    from hra_core.collections_utils import get_namedtuple_fields_as_list
    from hra_common.models import convert_file_specification
    from hra_common.models import FileSpecification
except ImportError as error:
    ImportErrorMessage(error, __name__)


class DatasourceFilesSpecificationModel(QStandardItemModel):

    def __init__(self):
        QStandardItemModel.__init__(self)
        self.setHorizontalHeaderLabels(
                            get_namedtuple_fields_as_list(FileSpecification))

    def appendRow(self, _path, _filename, _signal_index, _annotation_index,
                  _time_index, _separator, _signal_unit):
        row = [QStandardItem(QString(empty_string(item)))
                for item in [_path, _filename, _signal_index,
                             _annotation_index, _time_index, _separator]]
        row.append(QStandardItem(_signal_unit.__class__.__name__))
        super(DatasourceFilesSpecificationModel, self).appendRow(row)

    def fileSpecification(self, row):
        data = [str(self.item(row, column).text())
                for column in range(self.columnCount())]
        #because all data is in a string format there is the need
        #to convert to proper types of some member of file specification
        #tuple
        return convert_file_specification(FileSpecification(*data))

    def getAsFilesSpecifications(self):
        return  [self.fileSpecification(row) for row in range(self.rowCount())]
