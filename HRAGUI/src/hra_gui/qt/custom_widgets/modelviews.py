'''
Created on 13-12-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_common.models import FilePath
    from hra_gui.qt.utils.qt_i18n import QT_I18N
    from hra_gui.qt.utils.signals import SECTION_RESIZE_SIGNAL
    from hra_gui.qt.utils.signals import SECTION_MOVED_SIGNAL
    from hra_gui.qt.widgets.table_view_widget import TableViewWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class WidgetsHorizontalHeader(QHeaderView):
    """
    class for table header line used to create a header
    filled with widgets instead of simple texts
    widgets have to possess a layout
    """
    def __init__(self, parent):
        super(WidgetsHorizontalHeader, self).__init__(Qt.Horizontal, parent)
        self.parent = parent

        self.connect(self, SECTION_RESIZE_SIGNAL, self.handleSectionResized)
        self.connect(self, SECTION_MOVED_SIGNAL, self.handleSectionMoved)

        self.widgets = []
        self.parent.setHorizontalHeader(self)
        self.parent.setScrollContentsByHandler(self.__fixHeadersPositions__)

        self.__sizeHint__ = None

    def setWidgets(self, widgets):
        self.widgets = widgets

    def handleSectionResized(self, i):
        self.__show_sections__([self.logicalIndex(j)
            for j in range(self.visualIndex(i), self.count())])

    def handleSectionMoved(self, logical, oldVisualIndex, newVisualIndex):
        self.__show_sections__([self.logicalIndex(i)
            for i in range(min(oldVisualIndex, newVisualIndex), self.count())])

    def count(self):
        """
        get number of header widgets
        """
        return len(self.widgets)

    def showEvent(self, qShowEvent):
        self.__fixHeadersPositions__()
        super(WidgetsHorizontalHeader, self).showEvent(qShowEvent)

    def __fixHeadersPositions__(self):
        self.__show_sections__([i for i in range(self.count())])

    def __show_sections__(self, indexes):
        """
        the 'engine method' which set up the geometry of indexed elements
        of a header view
        """
        for i in indexes:
            self.widgets[i].setGeometry(self.sectionViewportPosition(i), 0,
                                    self.sectionSize(i) - 5, self.height())
            self.widgets[i].show()

    def sizeHint(self):
        """
        very important method, without this method widgets are displayed
        improperly, they have to fit in correct dimensions
        """
        #get optimal size for header line based on sizes of header widgets
        if self.__sizeHint__ == None:
            height = 0
            width = 0
            margin = 0
            for idx in range(len(self.widgets)):
                sizeHint = self.widgets[idx].sizeHint()
                if height < sizeHint.height():
                    height = sizeHint.height()
                if width < sizeHint.width():
                    width = sizeHint.width()
                if margin < self.widgets[idx].layout().margin():
                    margin = self.widgets[idx].layout().margin()

            self.__sizeHint__ = QSize(width + margin, height + margin)
        return self.__sizeHint__


class FilesTableView(object):
    def __init__(self, parent, **params):
        self.parent = parent
        self.__completed_count__ = 0
        self.selectedRow = None
        self.params = Params(**params)
        labels = ["",  # first column is checkable column
                  QT_I18N("datasource.files.column.filename", "Filename"),
                  QT_I18N("datasource.files.column.size", "Size"),
                  QT_I18N("datasource.files.column.path", "File path")]
        self.labels = QStringList(labels)

        self.filesTableView = TableViewWidget(parent,
                selectionBehavior=QAbstractItemView.SelectRows,
                selectionMode=QAbstractItemView.SingleSelection,
                enabled_precheck_handler=self.params.enabled_precheck_handler)
        if self.params.model:
            self.filesTableView.setModel(self.params.model)
        self.filesTableView.model().setHorizontalHeaderLabels(labels)
        self.filesTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        if self.params.onClickedAction:
            self.filesTableView.connect(self.filesTableView,
                                        SIGNAL('clicked(QModelIndex)'),
                                        self.params.onClickedAction)
            if not self.filesTableView.model() == None:
                #a signal used when selected row state is changed
                self.filesTableView.connect(self.filesTableView.model(),
                                        SIGNAL('itemChanged(QStandardItem *)'),
                                        self.__itemChanged__)
        if self.params.sorting:
            self.filesTableView.setSortingEnabled(True)

    def reload(self):
        if self.filesTableView.model().rowCount() > 0:
            self.filesTableView.resizeColumnsToContents()
            self.filesTableView.scrollToTop()

    def __itemChanged__(self, item):
        self.changeCompleteState(1, 'add'
                if item.checkState() == Qt.Checked else 'sub')

    def addRow(self, row):
        self.filesTableView.model().appendRow(row)

    def clear(self):
        self.filesTableView.model().removeRows(0,
                                    self.filesTableView.model().rowCount())
        self.minCompleteState()

    def getSelectedPathAndFilename(self):
        return self.getPathAndFilename(self.selectedRow)

    def getPathAndFilename(self, modelIdx):
        if not modelIdx == None:
            model = modelIdx.model()
            path = model.item(modelIdx.row(), 3)
            filename = model.item(modelIdx.row(), 1)
            return FilePath(str(path.text()), str(filename.text()))

    def onClickedAction(self, selectedRow):
        self.selectedRow = selectedRow
        #do not remove leave as an useful example
        #checked = self.__rowChecked__(selectedRow)

    def getSelectedItems(self):
        return [self.filesTableView.model().item(row)
                for row in range(0, self.filesTableView.model().rowCount())
        if self.filesTableView.model().item(row).checkState() == Qt.Checked]

    def setCheckedRowState(self, idx, state):
        self.filesTableView.model().item(idx).setCheckState(state)

    def getRowCount(self):
        return self.filesTableView.model().rowCount()

    def setEnabled(self, enabled):
        self.filesTableView.setEnabled(enabled)

    def resizeColumnsToContents(self):
        self.filesTableView.resizeColumnsToContents()

    def changeCompleteState(self, value=0, operation='set'):
        """
        a method instead of emitting a signal completeChanged() which
        is intercepted by QWizard to enable/disable next, previous buttons
        based on value returned by isComplete method of a wizard page

        set up wizard operational's buttons enable states, because use of
        the completeChange signal causes jump to the beginning of
        a table view instead of sticking to the position where it was already
        and also dim of a selected row is observed
        """
        if operation == 'set' and value != 0:
            self.__completed_count__ = value
        elif operation == 'add':
            self.__completed_count__ = self.__completed_count__ + value
        elif operation == 'sub':
            if self.__completed_count__ - value >= 0:
                self.__completed_count__ = self.__completed_count__ - value

        #self.emit(SIGNAL("completeChanged()"))
        if self.params.wizardButtons and self.params.wizard_handler:
            for button in self.params.wizardButtons:
                self.params.wizard_handler().button(button).setEnabled(
                                                    self.isCompletedCount())

    def isCompletedCount(self):
        return self.getCompletedCount() > 0

    def getCompletedCount(self):
        return self.__completed_count__

    def maxCompleteState(self):
        self.changeCompleteState(self.getRowCount())

    def minCompleteState(self):
        self.changeCompleteState(0)

    def getModel(self):
        return self.filesTableView.model()

    def setColumnHidden(self, column, hide=True):
        self.filesTableView.setColumnHidden(column, hide)

    def getSelectedRow(self):
        return self.selectedRow

    def model(self):
        return self.filesTableView.model()

    def count(self):
        return self.filesTableView.model().rowCount()

    def getSelectedRowCount(self):
        return len(self.filesTableView.selectedIndexes()) / len(self.labels)

    def selectRow(self, row, emulate_click=True):
        self.filesTableView.selectRow(row)
        if emulate_click:
            model = self.filesTableView.model()
            for column in range(model.columnCount()):
                if self.filesTableView.isColumnHidden(column) == False:
                    #simulate a click on the first visible column
                    self.filesTableView.emit(SIGNAL('clicked(QModelIndex)'),
                                         model.index(row, column))
                    break

#    def __rowChecked__(self, selectedRow):
#        """
#        method not used but stayed as an useful example
#        """
#        return self.filesTableView.model().item(
#                                selectedRow.row()).checkState() == Qt.Checked


class CheckStateProxySortFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(CheckStateProxySortFilterModel, self).__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        return self.sourceModel().item(source_row).checkState() == Qt.Checked # @IgnorePep8

    def __getattr__(self, name):
        """
        delegate calls method to source model
        """
        return getattr(self.sourceModel(), name)
