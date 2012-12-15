'''
Created on 13-12-2012

@author: jurek
'''
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pycore.misc import Params
from pygui.qt.utils.widgets import createTableView
from pygui.qt.utils.qt_i18n import QT_I18N


class WidgetsHorizontalHeader(QHeaderView):
    """
    class for table header line used to create a header
    filled with widgets instead of simple texts
    widgets have to possess a layout
    """
    def __init__(self, parent, widgets):
        super(WidgetsHorizontalHeader, self).__init__(Qt.Horizontal, parent)

        #get optimal size for header line based on sizes of header widgets
        height = 0
        width = 0
        margin = 0
        for idx in range(len(widgets)):
            sizeHint = widgets[idx].sizeHint()
            if height < sizeHint.height():
                height = sizeHint.height()
            if width < sizeHint.width():
                width = sizeHint.width()
            if margin < widgets[idx].layout().margin():
                margin = widgets[idx].layout().margin()

        #very import property used in sizeHint method
        self.sizeHint = QSize(width + margin, height + margin)

        self.setResizeMode(QHeaderView.Interactive)
        parent.setHorizontalHeader(self)
        self.widgets = widgets
        for idx in range(len(self.widgets)):
            widgets[idx].setParent(self)
            x = self.sectionPosition(idx)
            y = 0
            w = self.sectionSize(idx)  # widgets[idx].sizeHint().width()
            h = height
            widgets[idx].setGeometry(QRect(x, y, w, h))

        #if a header (or section) changes then widgets have to be moved
        self.connect(self,
                     SIGNAL("sectionResized(int,int,int)"),
                     self.sectionResized)

    def sizeHint(self):
        """
        very important method without it no widgets are displayed
        """
        return self.sizeHint

    def sectionResized(self, logicalIndex, oldSize, newSize):
        """
        a section means one header
        """
        old = self.widgets[logicalIndex].geometry()
        self.widgets[logicalIndex].setGeometry(old.x(), old.y(),
                                               newSize, old.height())
        #have to move the following headers about difference
        #between old and new size
        for idx in range(logicalIndex + 1, len(self.widgets)):
            self.changeXForHeader(idx, newSize - oldSize)

    def changeXForHeader(self, logicalIndex, x):
        """
        parameter x could be positive move to right
        or negative move to left
        """
        old = self.widgets[logicalIndex].geometry()
        self.widgets[logicalIndex].setGeometry(old.x() + x, old.y(),
                                            old.width(), old.height())


class FilesTableView(object):
    def __init__(self, parent, **params):
        self.parent = parent
        self.__completed_count__ = 0
        self.selectedRow = None
        self.params = Params(**params)
        if self.params.model:
            self.model = self.params.model
        self.proxyModel = self.params.proxyModel if self.params.proxyModel \
                            else None
        if self.proxyModel:
            self.proxyModel.setSourceModel(self.model)
            self.proxyModel.setDynamicSortFilter(True)
        labels = ["",  # first column is checkable column
                  QT_I18N("datasource.files.column.filename", "Filename"),
                  QT_I18N("datasource.files.column.size", "Size"),
                  QT_I18N("datasource.files.column.path", "File path")]
        labels = QStringList(labels)
        self.model.setHorizontalHeaderLabels(labels)
        self.filesTableView = createTableView(parent,
                        selectionBehavior=QAbstractItemView.SelectRows,
                        selectionMode=QAbstractItemView.SingleSelection)
        if self.proxyModel:
            self.filesTableView.setModel(self.proxyModel)
        else:
            self.filesTableView.setModel(self.model)
        self.filesTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        if self.params.onClickedAction:
            self.filesTableView.connect(self.filesTableView,
                                        SIGNAL('clicked(QModelIndex)'),
                                        self.params.onClickedAction)
        if self.params.sorting:
            self.filesTableView.setSortingEnabled(True)

    def reload(self):
        if self.model.rowCount() > 0:
            self.filesTableView.resizeColumnsToContents()
            self.filesTableView.scrollToTop()

    def addRow(self, row):
        self.model.appendRow(row)

    def clear(self):
        self.model.removeRows(0, self.model.rowCount())
        self.minCompleteState()

    def rowChecked(self, selectedRow):
        return self.model.item(selectedRow.row()).checkState() == Qt.Checked

    def getSelectedPathAndFilename(self, as_str=False):
        if not self.selectedRow == None:
            model = self.selectedRow.model()
            path = model.item(self.selectedRow.row(), 3)
            filename = model.item(self.selectedRow.row(), 1)
            if as_str == True:
                return (str(path.text()), str(filename.text()))
            else:
                return (path.text(), filename.text())

    def onClickedAction(self, selectedRow):
        self.selectedRow = selectedRow
        checked = self.rowChecked(selectedRow)
        self.changeCompleteState(1, 'add' if checked else 'sub')

    def getSelectedItems(self):
        return [self.model.item(row)
                for row in range(0, self.model.rowCount())
                    if self.model.item(row).checkState() == Qt.Checked]

    def setCheckedRowState(self, idx, state):
        self.model.item(idx).setCheckState(state)

    def getRowCount(self):
        return self.model.rowCount()

    def setEnabled(self, enabled):
        self.filesTableView.setEnabled(enabled)

    def resizeColumnsToContents(self):
        self.filesTableView.resizeColumnsToContents()

    def changeCompleteState(self, value, operation='set'):
        """
        method used to emit a signal completeChanged() which is intercepted
        by QWizard to enable/disable next, previous buttons based on value
        returned by isComplete method of a wizard page object
        correction:
        it's better do not send a completeChange signal, because
        program jump to the beginning of a table view instead of sticking
        to the position where it is already
        """
        if operation == 'set':
            self.__completed_count__ = value
        elif operation == 'add':
            self.__completed_count__ = self.__completed_count__ + value
        elif operation == 'sub':
            if self.__completed_count__ - value >= 0:
                self.__completed_count__ = self.__completed_count__ - value

        #self.emit(SIGNAL("completeChanged()"))
        if self.params.wizardButtons:
            for button in self.params.wizardButtons:
                self.params.wizard.button(button).setEnabled(
                                                self.__completed_count__ > 0)

    def getCompletedCount(self):
        return self.__completed_count__ > 0

    def maxCompleteState(self):
        self.changeCompleteState(self.getRowCount())

    def minCompleteState(self):
        self.changeCompleteState(0)

    def getModel(self):
        return self.model

    def setColumnHidden(self, column, hide=True):
        self.filesTableView.setColumnHidden(column, hide)

    def getSelectedRow(self):
        return self.selectedRow


class CheckStateProxySortFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(CheckStateProxySortFilterModel, self).__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        return self.sourceModel().item(source_row).checkState() == Qt.Checked # @IgnorePep8

    def item(self, row, column=0):
        return self.sourceModel().item(row, column)
