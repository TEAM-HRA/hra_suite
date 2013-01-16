'''
Created on 03-11-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.settings import SettingsFactory
from pygui.qt.utils.settings import Setter
from pygui.qt.utils.widgets import *  # @UnusedWildImport
from pygui.qt.utils.graphics import get_width_of_n_letters
from pycore.io_utils import is_text_file
from pycore.io_utils import DataFileHeader
from pygui.qt.custom_widgets.separator import DataSeparatorWidget
from pygui.qt.custom_widgets.progress_bar import ProgressBarManager
from pygui.qt.utils.windows import showFilePreviewDialog
from pygui.qt.utils.windows import InformationWindow
from pygui.qt.utils.windows import ErrorWindow
from pygui.qt.custom_widgets.modelviews import FilesTableView
from pygui.qt.custom_widgets.modelviews import WidgetsHorizontalHeader
from pygui.qt.custom_widgets.modelviews import CheckStateProxySortFilterModel
from pygui.qt.models.datasources import DatasourceFilesSpecificationModel
from pycore.collections import create_list
from pygui.qt.utils.signals import WIZARD_COMPLETE_CHANGED_SIGNAL
from pygui.qt.utils.plugins import PluginsManager
from pygui.qt.utils.plugins import PluginsNames


class DatasourceWizard(QWizard):

    @staticmethod
    def show_wizard(dargs):
        parent = dargs.get('parent', None)
        return DatasourceWizard(parent).show()

    def __init__(self, _parent):
        QWizard.__init__(self, _parent)
        self.setOptions(QWizard.NoBackButtonOnStartPage)
        self.setWizardStyle(QWizard.ModernStyle)
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setWindowTitle(QT_I18N("datasource.import.title",
                                    _default="Datasource import"))

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
        self.emit(WIZARD_COMPLETE_CHANGED_SIGNAL)
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

        self.changeEnablemend(False)
        self.chooseRootDirButton.setEnabled(True)

    def __createFileConstraintsComposite__(self, parent):
        fileConstraintsComposite = createComposite(parent,
                                                   layout=QHBoxLayout())

        self.chooseRootDirButton = createPushButton(fileConstraintsComposite,
                        i18n="datasource.datasource.choose.root.dir.button",
                        i18n_def="Choose root dir",
                        clicked_handler=self.chooseRootDirAction)

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
                        text="*",
                        enabled_precheck_handler=self.enabledPrecheckHandler)
        self.connect(self.filesExtension,
                     SIGNAL("textChanged(const QString&)"),
                     self.reload)

        self.recursively = createCheckBox(fileConstraintsComposite,
                        i18n="datasource.search.files.recursively.label",
                        i18n_def="Search files recursively",
                        clicked_handler=self.reload,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

        self.onlyKnownTypes = createCheckBox(fileConstraintsComposite,
                        i18n="datasource.only.known.types.checkbox",
                        i18n_def="Only known types",
                        checked=True,
                        clicked_handler=self.reload,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

    def __createReloadButton__(self, parent):
        self.reloadButton = createPushButton(parent,
                        i18n="datasource.reload.button",
                        i18n_def="Reload",
                        clicked_handler=self.reload,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

    def __createTableView__(self, parent):
        self.filesTableView = FilesTableView(parent,
                        model=QStandardItemModel(self),
                        onClickedAction=self.onClickedAction,
                        wizardButtons=(QWizard.NextButton,),
                        wizard=self.wizard(),
                        sorting=True,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

    def __createProgressBarComposite__(self, parent):
        self.progressBarManager.setParams(parent, hidden=True)

    def __createFilesOperationsComposite__(self, parent):
        filesOperations = createComposite(parent,
                                            layout=QHBoxLayout())

        self.filePreviewButton = createPushButton(filesOperations,
                        i18n="datasource.file.preview.button",
                        i18n_def="File preview",
                        stretch_after_widget=1,
                        clicked_handler=self.filePreviewAction,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

        self.checkAllButton = createPushButton(filesOperations,
                        i18n="datasource.accept.check.all.button",
                        i18n_def="Check all",
                        enabled=False,
                        clicked_handler=self.checkAllAction,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

        self.uncheckAllButton = createPushButton(filesOperations,
                        i18n="datasource.accept.uncheck.all.button",
                        i18n_def="Uncheck all",
                        enabled=False,
                        clicked_handler=self.uncheckAllAction,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

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
        self.progressBarManager.start(before=self.beforeProgressBarAction,
                                      progressJob=self.checkProgressBarAction,
                                      after=self.afterProgressBarAction)

    def uncheckAllAction(self):
        self.progressBarManager.start(
                                    before=self.beforeProgressBarAction,
                                    progressJob=self.uncheckProgressBarAction,
                                    after=self.afterProgressBarAction)

    def filePreviewAction(self):
        showFilePreviewDialog(
                    self.filesTableView.getSelectedPathAndFilename(False))

    def reload(self):
        if self.rootDirLabel.text():
            self.progressBarManager.start(
                    before=self.beforeTableViewProgressAction,
                    progressJob=self.tableViewProgressBarAction,
                    after=self.afterTableViewProgressAction)

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

    def afterTableViewProgressAction(self):
        self.filesTableView.resizeColumnsToContents()
        self.filesExtension.setFocus()
        self.changeEnablemend(True)

    def onClickedAction(self, idx):
        self.filePreviewButton.setEnabled(True)
        self.filesTableView.onClickedAction(idx)

    def isComplete(self):
        """
        method used by QWizard to check if next/previous buttons have to
        be disabled/enabled (when False/True is returned)
        """
        return self.filesTableView.isCompletedCount()

    def changeEnablemend(self, enabled):
        self.emit(SIGNAL(ENABLED_SIGNAL_NAME), enabled)
        self.chooseRootDirButton.setEnabled(enabled)

    def enabledPrecheckHandler(self, widget):
        """
        only interested widgets return bool value others none value
        """
        if widget in (self.checkAllButton, self.uncheckAllButton):
            return self.filesTableView.count() > 0
        elif widget == self.filePreviewButton:
            return self.filesTableView.getSelectedRowCount() > 0

    def beforeProgressBarAction(self):
        self.changeEnablemend(False)

    def checkProgressBarAction(self):
        self.__checkingProgressBarAction__(Qt.Checked)

    def afterProgressBarAction(self):
        self.filesTableView.changeCompleteState()
        self.changeEnablemend(True)

    def uncheckProgressBarAction(self):
        self.__checkingProgressBarAction__(Qt.Unchecked)

    def __checkingProgressBarAction__(self, checked):
        for idx in range(self.filesTableView.getRowCount()):
            if self.progressBarManager.update() == False:
                break
            self.filesTableView.setCheckedRowState(idx, checked)

    def getDatasourceModel(self):
        return self.filesTableView.getModel()


class ChooseColumnsDataPage(QWizardPage):

    def __init__(self, _parent, datasource_page_id):
        QWizardPage.__init__(self, parent=_parent)
        self.datasource_page_id = datasource_page_id
        self.pageLayout = None
        self.headersTablePreview = None

        self.__dataFilesHeaders__ = {}
        self.__dataColumnIndexes__ = {}  # includes selected data column indexes @IgnorePep8
        self.__annotationColumnIndexes__ = {}  # includes selected annotation column indexes @IgnorePep8        

        self.__globalSeparator__ = None
        self.__globalCheckBox__ = None
        self.__globalIndex__ = None

        self.__headerWidgets__ = []
        self.__widgetsHorizontalHeader__ = None

    def initializePage(self):
        self.setTitle('Choose column data')
        #self.setSubTitle('Choose column specific data')

        if self.pageLayout == None:
            self.pageLayout = QVBoxLayout()
            self.setLayout(self.pageLayout)
            self.__createTableView__(self.pageLayout)
        #select the first row
        self.filesTableView.selectRow(0)

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
                            enabled=False,
                            clicked_handler=self.filePreviewAction)

        self.separatorWidget = DataSeparatorWidget(self.tableViewComposite,
                                separatorHandler=self.__separatorHandler__,
                                globalHandler=self.__globalSeparatorHandler__,
                                enabled=False)

        self.__createHeaderPreviewGroup__()

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
        showFilePreviewDialog(
                        self.filesTableView.getSelectedPathAndFilename(False))

    def __separatorHandler__(self, _separator):
        self.__createFileHeadersPreview__(_separator)

    def __globalSeparatorHandler__(self, _checked, _separator=None):
        self.__globalSeparator__ = _separator

    def __createFileHeadersPreview__(self, _separator=None):

        dataFileHeader = self.__getDataFileHeader__(_separator)
        if dataFileHeader == None:
            return

        self.__createHeadersTablePreview__()

        colCount = dataFileHeader.getHeadersCount()
        model = self.__createHeadersTablePreviewModel__(colCount)

        self.__widgetsHorizontalHeader__ = WidgetsHorizontalHeader(
                                                    self.headersTablePreview)

        # create header line
        pathFile = self.filesTableView.getSelectedPathAndFilename()
        self.__headerWidgets__ = []
        for headerLine in dataFileHeader.getHeadersLines(1):
            for num, header in enumerate(headerLine):
                widget = HeaderWidget(self.__widgetsHorizontalHeader__,
                                      header,
                                      self.__dataWidgetHandler__,
                                      self.__annotationWidgetHandler__)
                self.__headerWidgets__.append(widget)
                if self.__globalIndex__:
                    widget.enabledAll(False)
                    if self.__globalIndex__[0] == num:  # data index
                        widget.check(HeaderWidget.DATA_TYPE)
                    if self.__globalIndex__[1] == num:  # annotation index
                        widget.check(HeaderWidget.ANNOTATION_TYPE)
                elif self.__dataColumnIndexes__.get(pathFile) == num:
                    widget.check(HeaderWidget.DATA_TYPE)
                elif self.__annotationColumnIndexes__.get(pathFile) == num:
                    widget.check(HeaderWidget.ANNOTATION_TYPE)
        self.__widgetsHorizontalHeader__.setWidgets(self.__headerWidgets__)

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
        pathFile = self.filesTableView.getSelectedPathAndFilename()
        if pathFile == None:
            ErrorWindow(message="The file must be selected !")
        else:
            return self.__createDataFileHeader__(pathFile, _separator)

    def __createHeadersTablePreviewModel__(self, colNumber):
        model = PreviewDataViewModel(self.headersTablePreview)
        labels = QStringList(create_list("", colNumber))
        model.setHorizontalHeaderLabels(labels)
        self.headersTablePreview.setModel(model)
        return model

    def __createHeadersTablePreview__(self):

        self.__createHeaderPreviewGroup__()

        self.headersTablePreview = createTableView(self.fileHeaderPreviewGroup,
                            selectionBehavior=QAbstractItemView.SelectRows,
                            selectionMode=QAbstractItemView.SingleSelection)

        self.__globalCheckBox__ = createCheckBox(
                                    self.fileHeaderPreviewGroup,
                                    i18n="global.data.column.index",
                                    i18n_def="Global columns indexes",
                                    clicked_handler=self.__globalClicked__)
        if self.__globalIndex__:
            self.__globalCheckBox__.setCheckState(Qt.Checked)

    def __createDataFileHeader__(self, pathFile, _separator):
        dataFileHeader = self.__dataFilesHeaders__.get(pathFile, None)
        if dataFileHeader == None:
            dataFileHeader = DataFileHeader(pathFile)
            self.__dataFilesHeaders__[pathFile] = dataFileHeader

        if _separator == None:
            _separator = dataFileHeader.getSeparator()

        if _separator == None:
            #try to discover a separator based on file data
            _separator = dataFileHeader.getSeparator(generate=True)

        dataFileHeader.setSeparator(_separator)
        return dataFileHeader

    def __getSelectedSeparator__(self):
        pathFile = self.filesTableView.getSelectedPathAndFilename()
        if pathFile:
            dataFileHeader = self.__dataFilesHeaders__.get(pathFile)
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

    def __dataWidgetHandler__(self, _widget):
        self.__widgetHandler__(_widget,
                               HeaderWidget.DATA_TYPE,
                               HeaderWidget.ANNOTATION_TYPE)

    def __annotationWidgetHandler__(self, _widget):
        self.__widgetHandler__(_widget,
                               HeaderWidget.ANNOTATION_TYPE,
                               HeaderWidget.DATA_TYPE)

    def __widgetHandler__(self, _widget, _type, _second_type):
        checked = _widget.isChecked(_type)
        if checked:
            for num, widget in enumerate(self.__headerWidgets__):
                if widget == _widget:
                    widget.uncheck(_second_type)
                    pathFile = self.filesTableView.getSelectedPathAndFilename()
                    if _type == HeaderWidget.DATA_TYPE:
                        self.__dataColumnIndexes__[pathFile] = num
                    else:
                        self.__annotationColumnIndexes__[pathFile] = num
                elif widget.isChecked(_type):
                    widget.uncheck(_type)
            self.__globalCheckBox__.setEnabled(True)

    def __globalClicked__(self):
        if self.__globalCheckBox__.checkState() == Qt.Checked:
            data_index = None
            annotation_index = None
            for num, widget in enumerate(self.__headerWidgets__):
                if widget.isChecked(HeaderWidget.DATA_TYPE):
                    data_index = num
                if widget.isChecked(HeaderWidget.ANNOTATION_TYPE):
                    annotation_index = num
            if data_index == None:
                self.__globalCheckBox__.setCheckState(Qt.Unchecked)
                InformationWindow(None,
                        message='At least data column has to be selected !')
            else:
                for num, widget in enumerate(self.__headerWidgets__):
                    widget.enabledAll(False)
                self.__globalIndex__ = (data_index, annotation_index)
                self.__setGlobalIndexForAll__(self.__globalIndex__)
        else:
            for widget in self.__headerWidgets__:
                widget.enabledAll(True)
            self.__globalIndex__ = None

    def __setGlobalIndexForAll__(self, _globalIndex):
        model = self.filesTableView.model()
        for row in range(model.rowCount()):
            #it's necessity to alter model index of QSortFilterProxyModel type
            #into source model index of QStandardItemModel type
            idx = model.mapToSource(model.index(row, 0))
            pathFile = self.filesTableView.getPathAndFilename(idx,
                                                         as_str=True)
            if pathFile:
                self.__dataColumnIndexes__[pathFile] = _globalIndex[0]
                if _globalIndex[1]:  # annontation global index
                    self.__annotationColumnIndexes__[pathFile] = \
                                                    _globalIndex[1]

    def __createHeaderPreviewGroup__(self):
        if hasattr(self, 'fileHeaderPreviewGroup'):
            self.fileHeaderPreviewGroup.deleteLater()
        self.fileHeaderPreviewGroup = createGroupBox(self.tableViewComposite,
                                    i18n="datasource.file.header.preview",
                                    i18n_def="Header preview",
                                    layout=QVBoxLayout(),
                                    hidden=True,
                                    enabled=False)

    def validatePage(self):
        filesSpecificationModel = DatasourceFilesSpecificationModel()
        for (_path, _filename, _dataIndex, __annotationIndex, _separator) in \
            self.__getFilesSpec__(indexes=True, separators=True):
                if _dataIndex == None:
                    ErrorWindow(message=("No data column for the file %s !"
                                         % (_filename)))
                    return False
                if _separator == None:
                    ErrorWindow(message=("No separator for file %s !"
                                         % (_filename)))
                    return False
                filesSpecificationModel.appendRow(_path, _filename, _dataIndex,
                                                __annotationIndex, _separator)

        PluginsManager.invokePlugin(PluginsNames.POINCARE_PLOT_PLUGIN_NAME,
                                    inspect.stack(),
                                    model=filesSpecificationModel)
        return True

    def __getFilesSpec__(self, _pathfile=True,
                         indexes=False, use_global_index=True,
                         separators=False, use_global_separator=True):
        filesSpec = []
        model = self.filesTableView.model()
        for row in range(model.rowCount()):
            #it's necessity to alter model index of QSortFilterProxyModel type
            #into source model index of QStandardItemModel type
            idx = model.mapToSource(model.index(row, 0))
            pathFile = self.filesTableView.getPathAndFilename(idx,
                                                         as_str=True)

            if pathFile:
                fileSpec = []
                if _pathfile == True:
                    fileSpec.extend(pathFile)

                if indexes == True:
                    dataIndex = self.__dataColumnIndexes__.get(pathFile)
                    if dataIndex == None and use_global_index == True and \
                        not self.__globalIndex__ == None:
                        dataIndex = self.__globalIndex__[0]
                    fileSpec.append(dataIndex)

                    annotationIndex = self.__annotationColumnIndexes__.get(
                                                                   pathFile)
                    if annotationIndex == None and use_global_index == True \
                        and not self.__globalIndex__ == None:
                        annotationIndex = self.__globalIndex__[1]
                    fileSpec.append(annotationIndex)
                if separators == True:
                    separator = None
                    dataFileHeader = self.__dataFilesHeaders__.get(pathFile)
                    if not dataFileHeader == None:
                        separator = dataFileHeader.getSeparator()
                    if separator == None and use_global_separator == True:
                        separator = self.__globalSeparator__
                    fileSpec.append(separator)
                filesSpec.append(tuple(fileSpec))
        return filesSpec


class HeaderWidget(QWidget):
    ANNOTATION_TYPE = 'a'
    DATA_TYPE = 'd'

    def __init__(self, _parent, _header, _dataHandler, _annotationHandler):
        QWidget.__init__(self, parent=_parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        createLabel(self, i18n_def=_header)
        self.dataButton = createCheckBox(self, i18n_def="data",
                                         clicked_handler=self.dataClicked)
        self.annotationButton = createCheckBox(self, i18n_def="annotation",
                                        clicked_handler=self.annotationClicked)

        self.__dataHandler__ = _dataHandler
        self.__annotationHandler__ = _annotationHandler

    def annotationClicked(self):
        self.__annotationHandler__(self)

    def dataClicked(self):
        self.__dataHandler__(self)

    def check(self, _type):
        self.__getButton__(_type).setCheckState(Qt.Checked)

    def uncheck(self, _type):
        self.__getButton__(_type).setCheckState(Qt.Unchecked)

    def isChecked(self, _type):
        return self.__getButton__(_type).checkState() == Qt.Checked

    def enabled(self, _type, _enabled):
        self.__getButton__(_type).setEnabled(_enabled)

    def enabledAll(self, _enabled):
        self.enabled(HeaderWidget.DATA_TYPE, _enabled)
        self.enabled(HeaderWidget.ANNOTATION_TYPE, _enabled)

    def __getButton__(self, _type):
        return self.dataButton if _type == HeaderWidget.DATA_TYPE \
                else self.annotationButton


class PreviewDataViewModel(QStandardItemModel):
    def __init__(self, parent):
        QStandardItemModel.__init__(self, parent=parent)

    def data(self, _modelIndex, _role):
        if _modelIndex.column() >= 0 and _role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        else:
            return super(PreviewDataViewModel, self).data(_modelIndex, _role)
