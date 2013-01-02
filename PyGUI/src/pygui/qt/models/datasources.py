'''
Created on 02-01-2013

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycore.collections import empty_string


class DatasourceFilesSpecificationModel(QStandardItemModel):
    def __init__(self):
        QStandardItemModel.__init__(self)
        labels = ["path", "filename", "data_index",
                  "annotation_index", "separator"]
        self.setHorizontalHeaderLabels(labels)

    def appendRow(self, _path, _filename, _dataIndex, _annotationIndex,
                  _separator):

        row = [QStandardItem(QString(empty_string(item)))
                for item in [_path, _filename, _separator, _dataIndex,
                             _annotationIndex]]
        super(DatasourceFilesSpecificationModel, self).appendRow(row)
