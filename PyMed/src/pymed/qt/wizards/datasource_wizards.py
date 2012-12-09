'''
Created on 03-11-2012

@author: jurek
'''
from os.path import join
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.qt_i18n import title_I18N
from pygui.qt.utils.widgets import createComposite
from pygui.qt.utils.widgets import ProgressBarManager
from pygui.qt.utils.widgets import createPlainTextEdit
from pygui.qt.utils.widgets import createTableView
from pygui.qt.utils.widgets import createLineEdit
from pygui.qt.utils.widgets import createCheckBox
from pygui.qt.utils.widgets import createLabel
from pygui.qt.utils.widgets import createPushButton
from pygui.qt.utils.widgets import createGroupBox
from pygui.qt.utils.graphics import get_width_of_n_letters
from pycore.io_utils import is_text_file
from pycore.misc import Params


class DatasourceWizard(QWizard):

    @staticmethod
    def show_wizard(dargs):
        parent = dargs.get('parent', None)
        return DatasourceWizard(parent).show()

    def __init__(self, _parent):
        QWizard.__init__(self, _parent)
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setWindowTitle(QT_I18N("datasource.import.title",
                                    _default="Datasource import"))
        self.datasourcePage = None

    def show(self):
        self.datasourcePage = ChooseDatasourcePage(self)
        id_ = self.addPage(self.datasourcePage)
        self.addPage(ChooseColumnsDataPage(self, id_))
        self.exec_()

    def closeEvent(self, event):
        self.datasourcePage.close()


class ChooseDatasourcePage(QWizardPage):

    def __init__(self, _parent):
        QWizardPage.__init__(self, parent=_parent)
        self.progressBarManager = ProgressBarManager()

    def closeEvent(self, event):
        self.progressBarManager.close()

    def hideEvent(self, event):
        self.progressBarManager.stop()

    def initializePage(self):
        title_I18N(self, "datasource.page.title", "Datasource chooser")
        #self.setSubTitle('Setup frame specific data')
        pageLayout = QVBoxLayout()
        self.setLayout(pageLayout)
        self.__createFilesGroupBox(pageLayout)

        #to force call of isComplete(self) method by the Wizard framework
        #which causes state next button to be updated
        self.emit(SIGNAL("completeChanged()"))

    def __createFilesGroupBox(self, pageLayout):
        self.filesGroupBox = createGroupBox(self,
                                    i18n="datasource.files.group.title",
                                    i18n_def="Files",
                                    layout=QVBoxLayout())

        self.__createFileConstraintsComposite__(self.filesGroupBox)

        self.__createReloadButton__(self.filesGroupBox)

        self.__createTableView__(self.filesGroupBox)

        self.__createProgressBarComposite__(self.filesGroupBox)

        self.__createFilesOperationsComposite__(self.filesGroupBox)

        self.changeEnablemend(False, withRootDir=False)

    def __createFileConstraintsComposite__(self, parent):
        fileConstraintsComposite = createComposite(parent,
                                                   layout=QHBoxLayout())

        self.chooseRootDirButton = createPushButton(fileConstraintsComposite,
                        i18n="datasource.datasource.choose.root.dir.button",
                        i18n_def="Choose root dir")
        self.connect(self.chooseRootDirButton, SIGNAL("clicked()"),
                     self.chooseRootDirAction)

        createLabel(fileConstraintsComposite,
                     i18n="datasource.root.dir.label",
                     i18n_def="Root dir:")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.rootDirLabel = createLabel(fileConstraintsComposite,
                                        i18n="datasource.root.dir.label",
                                        i18n_def="[Not set]",
                                        sizePolicy=sizePolicy,
                                        stretch_after_widget=1)

        createLabel(fileConstraintsComposite,
                    i18n="datasource.file.name.filter.label",
                    i18n_def="Files name filter")

        self.filesExtension = createLineEdit(fileConstraintsComposite,
                                             maxLength=15,
                                             width=get_width_of_n_letters(14),
                                             text="*")
        self.connect(self.filesExtension,
                     SIGNAL("textChanged(const QString&)"),
                     self.reload)

        self.recursively = createCheckBox(fileConstraintsComposite,
                i18n="datasource.search.files.recursively.label",
                i18n_def="Search files recursively")
        self.connect(self.recursively, SIGNAL("clicked()"),
                     self.reload)

        self.onlyKnownTypes = createCheckBox(fileConstraintsComposite,
                i18n="datasource.only.known.types.checkbox",
                i18n_def="Only known types",
                checked=True)
        self.connect(self.onlyKnownTypes, SIGNAL("clicked()"),
                     self.reload)

    def __createReloadButton__(self, parent):
        self.reloadButton = createPushButton(parent,
                                            i18n="datasource.reload.button",
                                            i18n_def="Reload")
        self.connect(self.reloadButton, SIGNAL("clicked()"),
                     self.reload)

    def __createTableView__(self, parent):
        self.filesTableView = FilesTableView(parent, self,
                                    onClickedAction=self.onClickedAction,
                                    wizardButtons=(QWizard.NextButton,),
                                    wizard=self.wizard(),
                                    sorting=True)

    def __createProgressBarComposite__(self, parent):
        self.progressBarManager.setParams(parent, hidden=True)

    def __createFilesOperationsComposite__(self, parent):
        filesOperations = createComposite(parent,
                                            layout=QHBoxLayout())

        self.filePreviewButton = createPushButton(filesOperations,
                            i18n="datasource.file.preview.button",
                            i18n_def="File preview",
                            stretch_after_widget=1,
                            enabled=False)
        self.connect(self.filePreviewButton, SIGNAL("clicked()"),
                     self.filePreviewAction)

        self.checkAllButton = createPushButton(filesOperations,
                            i18n="datasource.accept.check.all.button",
                            i18n_def="Check all")
        self.connect(self.checkAllButton, SIGNAL("clicked()"),
                     self.checkAllAction)

        self.uncheckAllButton = createPushButton(filesOperations,
                            i18n="datasource.accept.uncheck.all.button",
                            i18n_def="Uncheck all")
        self.connect(self.uncheckAllButton, SIGNAL("clicked()"),
                     self.uncheckAllAction)

    def chooseRootDirAction(self):
        rootDir = QFileDialog.getExistingDirectory(self,
                                    caption=self.chooseRootDirButton.text())
        if rootDir:
            self.rootDirLabel.setText(rootDir)
            self.reload()

    def checkAllAction(self):
        self.progressBarManager.start(before=self.beforeCheckProgressBarAction,
                                      progressJob=self.checkProgressBarAction,
                                      after=self.afterCheckProgressBarAction)

    def uncheckAllAction(self):
        self.progressBarManager.start(
                                    before=self.beforeUncheckProgressBarAction,
                                    progressJob=self.uncheckProgressBarAction,
                                    after=self.afterUncheckProgressBarAction)

    def filePreviewAction(self):
        pathFile = self.filesTableView.getSelectecPathAndFilename()
        if pathFile == None:
            QMessageBox.information(self, "Information",
                  "No files selected !")
        else:
            dialog = FilePreviewDialog(pathFile[0].text(),
                                       pathFile[1].text(), self)
            dialog.exec_()

    def reload(self):
        if self.rootDirLabel.text():
            self.progressBarManager.start(
                    before=self.beforeTableViewProgressAction,
                    progressJob=self.tableViewProgressBarAction,
                    after=self.afterFinishProgressBar)

    def beforeTableViewProgressAction(self):
        self.filesTableView.clear()
        self.changeEnablemend(False)

    def tableViewProgressBarAction(self):
        iteratorFlag = QDirIterator.Subdirectories \
                if self.recursively.checkState() == Qt.Checked \
                else QDirIterator.NoIteratorFlags

        nameFilters = QStringList(self.filesExtension.text()) \
                    if len(self.filesExtension.text()) > 0 \
                        and not self.filesExtension.text() \
                            in ("*", "*.*", "", None) \
                    else QStringList()

        self.dir_iterator = QDirIterator(self.rootDirLabel.text(),
                                    nameFilters,
                                    QDir.Filters(QDir.Files),
                                    iteratorFlag)
        while(self.dir_iterator.next()):
            if self.progressBarManager.update() == False:
                break
            infoFile = self.dir_iterator.fileInfo()
            if infoFile.isFile() == True and infoFile.size() > 0:
                if self.progressBarManager.isStopped() == True:
                    break
                if self.filesExtension.text() in ("*", "*.*", "", None):
                    if infoFile.isExecutable() == True or \
                        is_text_file(infoFile.filePath(),
                                    self.onlyKnownTypes.checkState()) == False:
                            continue
                checkable = QStandardItem("")
                checkable.setCheckable(True)
                filename = QStandardItem(infoFile.fileName())
                size = QStandardItem(str(infoFile.size()))
                path = QStandardItem(infoFile.path())
                if self.progressBarManager.isStopped() == True:
                    break
                self.filesTableView.addRow((checkable, filename, size, path))

    def afterFinishProgressBar(self):
        self.filesTableView.resizeColumnsToContents()
        self.changeEnablemend(True)
        self.filePreviewButton.setEnabled(False)
        self.filesExtension.setFocus()

    def onClickedAction(self, idx):
        self.filePreviewButton.setEnabled(True)
        self.filesTableView.onClickedAction(idx)

    def isComplete(self):
        """
        method used by QWizard to check if next/previous buttons have to
        be disabled/enabled (when False/True is returned)
        """
        return self.filesTableView.getCompletedCount()

    def changeEnablemend(self, enabled, withRootDir=True):
        self.filesExtension.setEnabled(enabled)
        self.recursively.setEnabled(enabled)
        self.filesTableView.setEnabled(enabled)
        self.checkAllButton.setEnabled(enabled)
        self.uncheckAllButton.setEnabled(enabled)
        self.reloadButton.setEnabled(enabled)
        self.onlyKnownTypes.setEnabled(enabled)
        self.filePreviewButton.setEnabled(enabled)
        if withRootDir == True:
            self.chooseRootDirButton.setEnabled(enabled)

    def beforeCheckProgressBarAction(self):
        self.changeEnablemend(False)

    def checkProgressBarAction(self):
        self.__stateProgressBarAction__(Qt.Checked)

    def afterCheckProgressBarAction(self):
        self.filesTableView.maxCompleteState()
        self.changeEnablemend(True)

    def beforeUncheckProgressBarAction(self):
        self.changeEnablemend(False)

    def uncheckProgressBarAction(self):
        self.__stateProgressBarAction__(Qt.Unchecked)

    def afterUncheckProgressBarAction(self):
        self.filesTableView.minCompleteState()
        self.changeEnablemend(True)

    def __stateProgressBarAction__(self, state):
        for idx in range(self.filesTableView.getRowCount()):
            if self.progressBarManager.update() == False:
                break
            self.filesTableView.setCheckedRowState(idx, state)

    def getDatasourceModel(self):
        return self.filesTableView.getModel()


class ChooseColumnsDataPage(QWizardPage):

    def __init__(self, _parent, datasource_page_id):
        QWizardPage.__init__(self, parent=_parent)
        self.datasource_page_id = datasource_page_id
        self.pageLayout = None

    def initializePage(self):
        self.setTitle('Choose column data')
        #self.setSubTitle('Choose column specific data')

        if self.pageLayout == None:
            self.pageLayout = QVBoxLayout()
            self.setLayout(self.pageLayout)
            self.__createTableView__(self.pageLayout)

    def __createTableView__(self, pageLayout):
        composite = createComposite(self, layout=QVBoxLayout())
        proxyModel = CheckStateProxySortFilterModel(self)
        datasource_page = self.wizard().page(self.datasource_page_id)
        model = datasource_page.getDatasourceModel()
        self.filesTableView = FilesTableView(composite, self,
                            onClickedAction=self.onClickedAction,
                            wizardButtons=(QWizard.NextButton,),
                            wizard=self.wizard(),
                            model=model,
                            proxyModel=proxyModel,
                            sorting=True)
        self.filesTableView.setColumnHidden(0, True)

    def onClickedAction(self, idx):
        pass


class FilePreviewDialog(QDialog):

    def __init__(self, path, filename, parent=None):
        super(FilePreviewDialog, self).__init__(parent)
        filename = QString(join(str(path), str(filename)))
        self.setWindowTitle('Preview of ' + filename)
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setLayout(QVBoxLayout())
        self.lineNumberLabel = createLabel(self)
        self.preview = createPlainTextEdit(self, readonly=True)

        closeButton = createPushButton(self,
                            i18n="close",
                            i18n_def="Close")
        self.connect(closeButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        file_ = QFile(QString(join(str(path), str(filename))))
        if file_.open(QFile.ReadOnly):
            self.preview.insertPlainText(QString(file_.readAll()))
            self.preview.moveCursor(QTextCursor.Start)
            self.lineNumberLabel.setText('Lines # '
                        + str(self.preview.document().lineCount()))
            file_.close()


class FilesTableView(object):
    def __init__(self, parent, parent_model, **params):
        self.parent = parent
        self.__completed_count__ = 0
        self.selectedRow = None
        self.params = Params(**params)
        if self.params.model:
            self.model = self.params.model
        else:
            self.model = QStandardItemModel(parent_model)
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

    def getSelectecPathAndFilename(self):
        if not self.selectedRow == None:
            model = self.selectedRow.model()
            path = model.item(self.selectedRow.row(), 2)
            filename = model.item(self.selectedRow.row(), 0)
            return (path, filename)

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


class CheckStateProxySortFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(CheckStateProxySortFilterModel, self).__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        return self.sourceModel().item(source_row).checkState() == Qt.Checked # @IgnorePep8
