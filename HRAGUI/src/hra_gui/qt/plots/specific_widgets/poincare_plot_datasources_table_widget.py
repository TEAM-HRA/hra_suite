'''
Created on 04-04-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_core.unicode_characters import HEAVY_CHECK_MARK
    from hra_core.collections_utils import get_or_put
    from hra_core.misc import Params
    from hra_core.io_utils import path_and_file
    from hra_gui.qt.widgets.table_view_widget import TableViewWidget
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PoincarePlotDatasourcesTableWidget(CompositeWidget):
    """
    a widget which displays selected poincare poincare plot datasource
    in a summary tachogram plots group widget
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Selected poincare plot datasources')
        super(PoincarePlotDatasourcesTableWidget, self).__init__(parent,
                                                                 **params)

        self.params = Params(**params)

        self.__createTable__()
        self.__createModel__()

    def __createTable__(self):
        self.__table__ = TableViewWidget(self)
        self.__table__.setSelectionMode(QAbstractItemView.MultiSelection)
        self.__table__.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.__table__.layout()

    def __createModel__(self):
        self.__table__.setModel(__PoincarePlotDatasourcesTableModel__(self))
        if self.params.data_accessors:
            for data_accessor in self.params.data_accessors:
                self.__table__.model().appendFile(data_accessor.source_name,
                                                  data_accessor.path_name)

    def appendFile(self, _filename):
        self.__table__.model().appendFile(_filename)

    def checkMarkFile(self, _filename):
        pass


class __PoincarePlotDatasourcesTableModel__(QStandardItemModel):
    """
    custom model for FilesTrackerWidget
    """
    def __init__(self, parent):
        QStandardItemModel.__init__(self, parent=parent)
        labels = QStringList([HEAVY_CHECK_MARK, "Filename ", "Path"])
        self.setHorizontalHeaderLabels(labels)

    def data(self, _modelIndex, _role):
#        if _modelIndex.column() == self.__size_column__ and \
#            _role == Qt.TextAlignmentRole:
#            return Qt.AlignRight
#        else:
        return super(__PoincarePlotDatasourcesTableModel__, self).data(
                                                        _modelIndex, _role)

    def appendFile(self, _filename, _pathname):

        if self.__find_row__(_pathname, _filename) == None:

            check_mark_column = QStandardItem("")

            filename_column = QStandardItem('%s' % _filename)
            filename_column.setCheckState(Qt.Unchecked)
            filename_column.setCheckable(True)

            pathname_column = QStandardItem(str(_pathname))

            self.appendRow([check_mark_column, filename_column,
                            pathname_column])

    def checkMarkFile(self, _fullfilename):
        _paf = path_and_file(_fullfilename)
        if _paf:
            row = self.__find_row__(_paf.pathname, _paf.filename)
            if row:
                check_mark_column = self.item(row, 0)
                check_mark_column.setText(str(HEAVY_CHECK_MARK))

#    def getSelectedFiles(self):
#        """
#        return selected filenames
#        """
#        selected_files = []
#        for row in range(self.rowCount()):
#            item = self.item(row)
#            if item.isCheckable() and item.checkState() == Qt.Checked:
#                selected_files.append(str(item.text()))
#        return selected_files

    def __find_row__(self, _pathname, _filename):
        filename_rows = set([self.indexFromItem(filename_item).row()
                for filename_item in self.findItems(_filename, column=1)])

        pathname_rows = set([self.indexFromItem(filename_item).row()
                for filename_item in self.findItems(_pathname, column=2)])
        rows = filename_rows & pathname_rows
        return None if len(rows) == 0 else list(rows)[0]  # a set don't have indexing operation @IgnorePep8
