'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.misc import Params
    from pycore.io_utils import normalize_filenames
    from pygui.qt.utils.windows import FilesPreviewDialog
    from pygui.qt.utils.constants import DATE_TIME_FORMAT
    from pygui.qt.widgets.table_view_widget import TableViewWidget
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class FilesTrackerWidget(CompositeWidget):
    """
    widget which tracks created files
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Files')
        super(FilesTrackerWidget, self).__init__(parent, **params)

        self.params = Params(**params)

        self.__create_oper_buttons__()
        self.__createTable__()
        self.__createModel__()
        self.__create_misc_buttons__()

    def __createTable__(self):
        self.__table__ = TableViewWidget(self,
                change_check_count_handler=self.__change_check_count_handler__,
                rows_inserted_handler=self.__rows_inserted_handler__)
        self.__table__.setSelectionMode(QAbstractItemView.MultiSelection)
        self.__table__.setSelectionBehavior(QAbstractItemView.SelectRows)

    def __createModel__(self):
        self.__table__.setModel(__FilesTrackerModel__(self))

    def __create_oper_buttons__(self):
        buttons_composite = CompositeWidget(self, layout=QHBoxLayout())
        self.__select_all__ = PushButtonWidget(buttons_composite,
                    i18n_def="Select all",
                    clicked_handler=self.__select_all_handler__,
                    enabled=False)

        self.__unselect_all__ = PushButtonWidget(buttons_composite,
                    i18n_def="Unselect all",
                    clicked_handler=self.__unselect_all_handler__,
                    enabled=False)

        self.__clear__ = PushButtonWidget(buttons_composite, i18n_def="Clear",
                    clicked_handler=self.__clear_handler__,
                    enabled=False)

    def __select_all_handler__(self):
        self.__table__.changeCheckStatForAll(True)

    def __unselect_all_handler__(self):
        self.__table__.changeCheckStatForAll(False)

    def __clear_handler__(self):
        self.__table__.clearRows()
        self.__select_all__.setEnabled(False)
        self.__unselect_all__.setEnabled(False)
        self.__clear__.setEnabled(False)
        self.__plain_view__.setEnabled(False)

    def appendFile(self, _filename):
        self.__table__.model().appendFile(_filename)

    def __create_misc_buttons__(self):
        buttons_composite = CompositeWidget(self, layout=QHBoxLayout())
        self.__plain_view__ = PushButtonWidget(buttons_composite,
                    i18n_def="Plain view",
                    clicked_handler=self.__plain_view_handler__,
                    enabled=False)

    def __plain_view_handler__(self):
        filesnames = self.__table__.model().getSelectedFiles()
        dialog = FilesPreviewDialog(normalize_filenames(filesnames), self)
        dialog.exec_()

    def __change_check_count_handler__(self, count):
        self.__plain_view__.setEnabled(count > 0)

    def __rows_inserted_handler__(self, model_index, start_row, end_row):
        self.__select_all__.setEnabled(True)
        self.__unselect_all__.setEnabled(True)
        self.__clear__.setEnabled(True)


class __FilesTrackerModel__(QStandardItemModel):
    """
    custom model for FilesTrackerWidget
    """
    def __init__(self, parent):
        QStandardItemModel.__init__(self, parent=parent)
        labels = QStringList(["File", "Size", "Modified"])
        self.setHorizontalHeaderLabels(labels)
        self.__size_column__ = 1

    def data(self, _modelIndex, _role):
        if _modelIndex.column() == self.__size_column__ and \
            _role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        else:
            return super(__FilesTrackerModel__, self).data(_modelIndex,
                                                              _role)

    def appendFile(self, _filename):

        file_info = QFileInfo(_filename)

        #update existing row (with the same filename)
        for row in range(self.rowCount()):
            filename_column = self.item(row, 0)
            if filename_column.text() == _filename:
                size_column = self.item(row, 1)
                size_column.setText(str(file_info.size()))

                file_time_column = self.item(row, 2)
                file_time = file_info.lastModified()
                file_time = file_time.toString(DATE_TIME_FORMAT) if file_time else "" # @IgnorePep8
                file_time_column.setText(str(file_time))
                return

        filename_column = QStandardItem('%s' % _filename)
        filename_column.setCheckState(Qt.Unchecked)
        filename_column.setCheckable(True)
        size_column = QStandardItem(str(file_info.size()))
        file_time = file_info.lastModified()
        file_time = file_time.toString(DATE_TIME_FORMAT) if file_time else ""
        file_time_column = QStandardItem(str(file_time))

        self.appendRow([filename_column, size_column, file_time_column])

    def getSelectedFiles(self):
        """
        return selected filenames
        """
        selected_files = []
        for row in range(self.rowCount()):
            item = self.item(row)
            if item.isCheckable() and item.checkState() == Qt.Checked:
                selected_files.append(str(item.text()))
        return selected_files
