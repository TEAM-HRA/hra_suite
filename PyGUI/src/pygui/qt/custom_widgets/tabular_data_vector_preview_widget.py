'''
Created on 26 maj 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.widgets.table_view_widget import TableViewWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TabularDataVectorPreviewWidget(TableViewWidget):
    """
    a widget used to display a data vector in convenient tabular view widget
    """
    def __init__(self, parent, **params):
        TableViewWidget.__init__(self, parent, **params)
        self.params = Params(**params)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__createModel__()

    def __createModel__(self):
        model = __TabularDataVectorPreviewModel__(self,
                                         self.params.data,
                                         self.params.headers)
        self.setModel(model)


class __TabularDataVectorPreviewModel__(QStandardItemModel):
    def __init__(self, parent, data, headers=None):
        QStandardItemModel.__init__(self, parent=parent)
        if headers == None:
            headers = [str(idx) for idx in range(1, len(data))]
        labels = QStringList(headers)
        self.setHorizontalHeaderLabels(labels)
        for row_data in zip(*data):
            self.appendRow([QStandardItem(str(data_item))
                                 for data_item in row_data])

    def data(self, _modelIndex, _role):
        if _role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        else:
            return super(__TabularDataVectorPreviewModel__, self).data(
                                                _modelIndex, _role)
