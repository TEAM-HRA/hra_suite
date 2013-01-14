'''
Created on 02-01-2013

@author: jurek
'''
import collections
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycore.collections import empty_string


class DatasourceFilesSpecificationModel(QStandardItemModel):

    labels = ["filepath", "filename", "data_index", "annotation_index", "separator"] # @IgnorePep8
    FileSpecification = collections.namedtuple('FileSpecification', labels)

    def __init__(self):
        QStandardItemModel.__init__(self)
        self.setHorizontalHeaderLabels(DatasourceFilesSpecificationModel.labels) # @IgnorePep8

    def appendRow(self, _path, _filename, _dataIndex, _annotationIndex,
                  _separator):
        row = [QStandardItem(QString(empty_string(item)))
                for item in [_path, _filename, _separator, _dataIndex,
                             _annotationIndex]]
        super(DatasourceFilesSpecificationModel, self).appendRow(row)

    def fileSpecification(self, row):
        data = [self.item(row, column).text()
                for column in range(self.columnCount())]
        return DatasourceFilesSpecificationModel.FileSpecification(*data)
