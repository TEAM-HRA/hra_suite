'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.signals import ITEM_CHANGED_SIGNAL
    from pygui.qt.widgets.commons import Common
    from pygui.qt.widgets.commons import prepareWidget
    from pygui.qt.custom_widgets.progress_bar import ProgressDialogManager
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TableViewWidget(QTableView, Common):
    def __init__(self, parent, **params):
        super(TableViewWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)
        self.params = Params(**params)
        self.__checked_count__ = 0

    @property
    def checked_count(self):
        """
        return number of rows at check state (if any)
        if return -1 than mean table view is not checkable
        """
        return self.__checked_count__ if self.is_checkable else -1

    @property
    def is_checkable(self):
        """
        return true if a table is checkable
        """
        model = self.model()
        if not model == None:
            for idx in range(model.rowCount()):
                if model.item(idx).isCheckable():
                    return True
        return False

    def changeCheckStatForAll(self, _check):
        """
        method changes check state (True/False) for the whole table view
        """
        if not self.is_checkable:
            return
        self.setEnabled(False)
        count = self.model().rowCount()
        progressManager = ProgressDialogManager(self,
                label_text=("Checking..." if _check else "Unchecking..."),
                max_value=count)
        with progressManager as progress:
            for idx in range(count):
                if (progress.wasCanceled()):
                    break
                progress.increaseCounter()
                self.model().item(idx).setCheckState(Qt.Checked
                                                if _check else Qt.Unchecked)
        self.setEnabled(True)

    def setModel(self, model):
        super(TableViewWidget, self).setModel(model)
        #signal used when selected row check state is changed
        self.connect(self.model(), ITEM_CHANGED_SIGNAL, self.__itemChanged__)

    def __itemChanged__(self, item):
        if item.isCheckable():
            if item.checkState() == Qt.Checked:
                self.__checked_count__ = self.__checked_count__ + 1
            else:
                self.__checked_count__ = self.__checked_count__ - 1
            if self.params.change_check_count_handler:
                self.params.change_check_count_handler(self.__checked_count__)
