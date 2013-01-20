'''
Created on 02-01-2013

@author: jurek
'''
import collections
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycore.collections import empty_string

FileSpecificationLabels = ["filepath", "filename", "data_index",
                           "annotation_index", "separator"]
FileSpecification = collections.namedtuple('FileSpecification',
                                           FileSpecificationLabels)


class DatasourceFilesSpecificationModel(QStandardItemModel):

    def __init__(self):
        QStandardItemModel.__init__(self)
        self.setHorizontalHeaderLabels(FileSpecificationLabels)

    def appendRow(self, _path, _filename, _dataIndex, _annotationIndex,
                  _separator):
        row = [QStandardItem(QString(empty_string(item)))
                for item in [_path, _filename, _separator, _dataIndex,
                             _annotationIndex]]
        super(DatasourceFilesSpecificationModel, self).appendRow(row)

    def fileSpecification(self, row):
        data = [str(self.item(row, column).text())
                for column in range(self.columnCount())]
        return FileSpecification(*data)
