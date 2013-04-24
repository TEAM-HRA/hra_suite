'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
from pygui.qt.custom_widgets.progress_bar import ProgressDialogManager
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.widgets.commons import Common
    from pygui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TableViewWidget(QTableView, Common):
    def __init__(self, parent, **params):
        super(TableViewWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)

    @property
    def checked_count(self):
        """
        return number of rows at check state (if any)
        if return -1 than mean table view is not checkable
        """
        count = -1
        if self.is_checkable:
            count = 0
            model = self.model()
            for idx in range(model.rowCount()):
                if model.item(idx).isCheckable():
                    if model.item(idx).checkState() == Qt.Checked:
                        count = count + 1
        return count

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
