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

        self.__createButtons__()
        self.__createTable__()
        self.__createModel__()

    def __createTable__(self):
        self.__table__ = TableViewWidget(self)
        self.__table__.setSelectionMode(QAbstractItemView.MultiSelection)
        self.__table__.setSelectionBehavior(QAbstractItemView.SelectRows)

    def __createModel__(self):
        self.__table__.setModel(__FilesTrackerModel__(self))

    def __createButtons__(self):
        buttons_composite = CompositeWidget(self, layout=QHBoxLayout())
        PushButtonWidget(buttons_composite, i18n_def="Select all",
                    clicked_handler=self.__select_all_handler__)

        PushButtonWidget(buttons_composite, i18n_def="Unselect all",
                    clicked_handler=self.__unselect_all_handler__)

        PushButtonWidget(buttons_composite, i18n_def="Clear",
                    clicked_handler=self.__clear_handler__)

    def __select_all_handler__(self):
        self.__table__.changeCheckStatForAll(True)

    def __unselect_all_handler__(self):
        self.__table__.changeCheckStatForAll(False)

    def __clear_handler__(self):
        self.__table__.clearRows()

    def appendFile(self, _filename):
        self.__table__.model().appendFile(_filename)


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

        filename_column = QStandardItem('%s' % _filename)
        filename_column.setCheckState(Qt.Unchecked)
        filename_column.setCheckable(True)
        size_column = QStandardItem(str(file_info.size()))
        file_time = file_info.lastModified()
        file_time = file_time.toString(DATE_TIME_FORMAT) if file_time else ""
        file_time_column = QStandardItem(str(file_time))

        self.appendRow([filename_column, size_column, file_time_column])
