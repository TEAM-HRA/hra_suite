'''
Created on 03-11-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.qt_i18n import title_I18N
from pygui.qt.utils.widgets import createComposite
from pygui.qt.utils.widgets import createTableView
from pygui.qt.utils.widgets import createLineEdit
from pygui.qt.utils.widgets import createCheckBox
from pygui.qt.utils.widgets import createLabel
from pygui.qt.utils.widgets import createPushButton
from pygui.qt.utils.widgets import createGroupBox
from pygui.qt.utils.graphics import get_width_of_n_letters
from pycore.io_utils import is_text_file
from pycore.io_utils import DataFileHeader
from pygui.qt.utils.settings import SettingsFactory
from pygui.qt.utils.settings import Setter
from pygui.qt.custom_widgets.separator import DataSeparatorWidget
from pygui.qt.custom_widgets.progress_bar import ProgressBarManager
from pygui.qt.utils.windows import showFilePreviewDialog
from pygui.qt.utils.windows import ErrorWindow
from pygui.qt.custom_widgets.modelviews import FilesTableView
from pygui.qt.custom_widgets.modelviews import WidgetsHorizontalHeader
from pygui.qt.custom_widgets.modelviews import CheckStateProxySortFilterModel
from pycore.collections import create_list


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
        self.rootDir = None

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
        self.filesTableView = FilesTableView(parent,
                                    model=QStandardItemModel(self),
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
        SettingsFactory.loadSettings(self, Setter(rootDir=None))

        rootDir = QFileDialog.getExistingDirectory(self,
                                    caption=self.chooseRootDirButton.text(),
                                    directory=self.rootDir)
        if rootDir:
            self.rootDir = rootDir
            SettingsFactory.saveSettings(self, Setter(rootDir=self.rootDir))
            self.rootDirLabel.setText(self.rootDir)
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
        showFilePreviewDialog(self.filesTableView.getSelectedPathAndFilename())

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
        self.headersTablePreview = None
        self.dataFilesHeaders = {}
        self.__globalSeparator__ = None

    def initializePage(self):
        self.setTitle('Choose column data')
        #self.setSubTitle('Choose column specific data')

        if self.pageLayout == None:
            self.pageLayout = QVBoxLayout()
            self.setLayout(self.pageLayout)
            self.__createTableView__(self.pageLayout)

    def __createTableView__(self, pageLayout):
        self.tableViewComposite = createComposite(self, layout=QVBoxLayout())

        datasource_page = self.wizard().page(self.datasource_page_id)
        model = CheckStateProxySortFilterModel(self)
        model.setSourceModel(datasource_page.getDatasourceModel())
        model.setDynamicSortFilter(True)

        self.filesTableView = FilesTableView(self.tableViewComposite,
                                        model=model,
                                        onClickedAction=self.onClickedAction,
                                        wizardButtons=(QWizard.NextButton,),
                                        wizard=self.wizard(),
                                        sorting=True)
        self.filesTableView.setColumnHidden(0, True)

        self.filePreviewButton = createPushButton(self.tableViewComposite,
                            i18n="datasource.file.preview.button",
                            i18n_def="File preview",
                            enabled=False)
        self.connect(self.filePreviewButton, SIGNAL("clicked()"),
                     self.filePreviewAction)

        self.separatorWidget = DataSeparatorWidget(self.tableViewComposite,
                                    separatorHandler=self.__separatorHandler__,
                                    globalHandler=self.__globalHandler__,
                                    enabled=False)

        self.fileHeaderPreviewGroup = createGroupBox(self.tableViewComposite,
                                    i18n="datasource.file.header.preview",
                                    i18n_def="Header preview",
                                    layout=QHBoxLayout(),
                                    hidden=True,
                                    enabled=False)

    def onClickedAction(self, idx):
        self.filePreviewButton.setEnabled(True)
        self.filesTableView.onClickedAction(
                                self.filesTableView.model().mapToSource(idx))
        #global separator could be None
        self.__createFileHeadersPreview__(self.__globalSeparator__)
        if self.__globalSeparator__:
            self.separatorWidget.setSeparator(self.__globalSeparator__)
        else:
            self.separatorWidget.setSeparator(self.__getSelectedSeparator__())
        self.separatorWidget.setEnabled(True)

    def filePreviewAction(self):
        showFilePreviewDialog(self.filesTableView.getSelectedPathAndFilename())

    def __separatorHandler__(self, _separator):
        self.__createFileHeadersPreview__(_separator)

    def __globalHandler__(self, _checked, _separator=None):
        self.__globalSeparator__ = _separator

    def __createFileHeadersPreview__(self, _separator=None):

        dataFileHeader = self.__getDataFileHeader__(_separator)
        if dataFileHeader == None:
            return

        self.__createHeadersTablePreview__()

        colCount = dataFileHeader.getHeadersCount()

        model = self.__createHeadersTablePreviewModel__(colCount)

        # create header line
        for headerLine in dataFileHeader.getHeadersLines(1):
            for colNum, header in enumerate(headerLine):
                self.__createHeaderWidget__(header, colNum)
        WidgetsHorizontalHeader(self.headersTablePreview, self.headerWidgets)

        # create data lines
        for rowData in dataFileHeader.getDataLines():
            modelData = list()
            for idx in range(colCount):
                modelData.append(QStandardItem(rowData[idx]
                                        if colCount <= len(rowData) else ""))
            model.appendRow(modelData)

        self.fileHeaderPreviewGroup.setEnabled(True)
        self.fileHeaderPreviewGroup.show()

    def __getDataFileHeader__(self, _separator=None):
        pathFile = self.filesTableView.getSelectedPathAndFilename(True)
        if pathFile == None:
            ErrorWindow(message="No file is selected !")
        else:
            return self.__createDataFileHeader__(pathFile, _separator)

    def __createHeadersTablePreviewModel__(self, colNumber):
        model = QStandardItemModel(self.headersTablePreview)
        labels = QStringList(create_list("", colNumber))
        model.setHorizontalHeaderLabels(labels)
        self.headersTablePreview.setModel(model)
        return model

    def __createHeaderWidget__(self, header, colNum):
        if colNum == 0:
            self.headerWidgets = []
        ChooseColumnsDataPage.HeaderWidget(self.headersTablePreview,
                                           header,
                                           colNum,
                                           self.headerWidgets)

    def __createHeadersTablePreview__(self):

        # remove previous instance of self.headersTablePreview
        if not self.headersTablePreview == None:
            self.fileHeaderPreviewGroup.layout().removeWidget(
                                                    self.headersTablePreview)
            self.headersTablePreview.destroy()

        self.headersTablePreview = createTableView(self.fileHeaderPreviewGroup,
                            selectionBehavior=QAbstractItemView.SelectRows,
                            selectionMode=QAbstractItemView.SingleSelection)

    def __createDataFileHeader__(self, pathFile, _separator):
        dataFileHeader = self.dataFilesHeaders.get(pathFile, None)
        if dataFileHeader == None:
            dataFileHeader = DataFileHeader(pathFile)
            self.dataFilesHeaders[pathFile] = dataFileHeader

        if _separator == None:
            _separator = dataFileHeader.getSeparator()

        if _separator == None:
            #try to discover a separator based on file data
            _separator = dataFileHeader.getSeparator(generate=True)

        dataFileHeader.setSeparator(_separator)
        return dataFileHeader

    def __getSelectedSeparator__(self):
        pathFile = self.filesTableView.getSelectedPathAndFilename(as_str=True)
        if pathFile:
            dataFileHeader = self.dataFilesHeaders.get(pathFile)
            if dataFileHeader:
                return dataFileHeader.getSeparator()

    # for future use
    def __setSeparatorForAll__(self, _separator=None):
        model = self.filesTableView.model()
        for row in range(model.rowCount()):
            #it's necessity to alter model index of QSortFilterProxyModel type
            #into source model index of QStandardItemModel type
            idx = model.mapToSource(model.index(row, 0))
            pathFile = self.filesTableView.getPathAndFilename(idx,
                                                         as_str=True)
            if pathFile:
                self.__createDataFileHeader__(pathFile, _separator)

    class HeaderWidget(QWidget):
        def __init__(self, _parent, _header, _colNum, _widgets):
            QWidget.__init__(self, parent=_parent)
            _widgets.append(self)
            self.widgets = _widgets
            self.colNum = _colNum
            layout = QVBoxLayout()
            layout.addWidget(QLabel(_header, self))
            self.dataButton = QCheckBox("data", self)
            layout.addWidget(self.dataButton)
            self.annotationButton = QCheckBox("annotation", self)
            layout.addWidget(self.annotationButton)
            self.setLayout(layout)
            self.connect(self.dataButton, SIGNAL("clicked()"),
                         self.dataClicked)
            self.connect(self.annotationButton, SIGNAL("clicked()"),
                         self.annotationClicked)

        def annotationClicked(self):
            if self.annotationButton.checkState() == Qt.Checked:
                self.uncheckData()
                for num, widget in enumerate(self.widgets):
                    if not num == self.colNum:
                        widget.uncheckAnnotation()

        def dataClicked(self):
            if self.dataButton.checkState() == Qt.Checked:
                self.uncheckAnnotation()
                for num, widget in enumerate(self.widgets):
                    if not num == self.colNum:
                        widget.uncheckData()

        def uncheckData(self):
            self.dataButton.setCheckState(Qt.Unchecked)

        def uncheckAnnotation(self):
            self.annotationButton.setCheckState(Qt.Unchecked)
