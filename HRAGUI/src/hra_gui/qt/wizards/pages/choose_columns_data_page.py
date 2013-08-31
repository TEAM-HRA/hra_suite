'''
Created on 03-11-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    import collections
    import inspect
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_core.collections_utils import create_list
    from hra_core.collections_utils import nvl
    from hra_core.io_utils import DataFileHeader
    from hra_gui.qt.activities.activities import ActivityWidget
    from hra_gui.qt.utils.windows import showFilesPreviewDialog
    from hra_gui.qt.utils.windows import InformationWindow
    from hra_gui.qt.utils.windows import ErrorWindow
    from hra_gui.qt.custom_widgets.modelviews import FilesTableView
    from hra_gui.qt.custom_widgets.modelviews import WidgetsHorizontalHeader
    from hra_gui.qt.custom_widgets.modelviews \
        import CheckStateProxySortFilterModel
    from hra_gui.qt.custom_widgets.global_separator_widget import GlobalSeparatorWidget # @IgnorePep8
    from hra_gui.qt.custom_widgets.units import TimeUnitsWidget
    from hra_gui.qt.models.datasources import DatasourceFilesSpecificationModel
    from hra_gui.qt.utils.plugins import PluginsManager
    from hra_gui.qt.utils.plugins import PluginsNames
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.check_box_widget import CheckBoxWidget
    from hra_gui.qt.widgets.table_view_widget import TableViewWidget
    from hra_gui.qt.widgets.group_box_widget import GroupBoxWidget
    from hra_gui.qt.custom_widgets.checkable_table_header_widget import HeaderElement # @IgnorePep8
    from hra_gui.qt.custom_widgets.checkable_table_header_widget import HeaderWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ChooseColumnsDataPage(QWizardPage):

    def __init__(self, _parent, datasource_page_id):
        QWizardPage.__init__(self, parent=_parent)
        self.datasource_page_id = datasource_page_id
        self.pageLayout = None
        self.headersTablePreview = None

        self.__dataFilesHeaders__ = {}
        self.__signalColumnIndexes__ = {}  # includes selected signal column indexes @IgnorePep8
        self.__annotationColumnIndexes__ = {}  # includes selected annotation column indexes @IgnorePep8
        self.__timeColumnIndexes__ = {}  # includes selected [optional] time column indexes @IgnorePep8

        self.__globalSeparator__ = None
        self.__globalCheckBox__ = None
        self.__globalIndex__ = GlobalIndex(None, None, None)

        self.__headerWidgets__ = []
        self.__widgetsHorizontalHeader__ = None

        self.__signal_header_element__ = HeaderElement('signal', 'signal', self.__signalWidgetHandler__) # @IgnorePep8
        self.__annotation_header_element__ = HeaderElement('annotation', 'annotation', self.__annotationWidgetHandler__) # @IgnorePep8
        self.__time_header_element__ = HeaderElement('time', 'time', self.__timeWidgetHandler__) # @IgnorePep8

    def initializePage(self):
        self.setTitle('Choose column data')
        #self.setSubTitle('Choose column specific data')

        if self.pageLayout == None:
            self.pageLayout = QVBoxLayout()
            self.setLayout(self.pageLayout)
            self.__createTableView__(self.pageLayout)
        #select the first row
        self.filesTableView.selectRow(0)
        self.separatorWidget.setGlobalSeparatorAsDefault()

    def __createTableView__(self, pageLayout):
        self.tableViewComposite = CompositeWidget(self, layout=QVBoxLayout())

        datasource_page = self.wizard().page(self.datasource_page_id)
        model = CheckStateProxySortFilterModel(self)
        model.setSourceModel(datasource_page.getDatasourceModel())
        model.setDynamicSortFilter(True)

        self.filesTableView = FilesTableView(self.tableViewComposite,
                                        model=model,
                                        onClickedAction=self.onClickedAction,
                                        wizardButtons=(QWizard.NextButton,),
                                        wizard_handler=self.wizard,
                                        sorting=True)
        self.filesTableView.setColumnHidden(0, True)

        self.filePreviewButton = PushButtonWidget(self.tableViewComposite,
                            i18n="datasource.file.preview.button",
                            i18n_def="File preview",
                            enabled=False,
                            clicked_handler=self.filePreviewAction)

        self.separatorWidget = GlobalSeparatorWidget(self.tableViewComposite,
                                separatorHandler=self.__separatorHandler__,
                                globalHandler=self.__globalSeparatorHandler__,
                                enabled=False)

        self.__createHeaderPreviewGroup__()

        self.__activity__ = ActivityWidget(self)

        self.__timeUnitsGroup__ = self.__createTimeUnitsGroup__()

    def __createTimeUnitsGroup__(self):
        return TimeUnitsWidget(self.tableViewComposite,
                               i18n_def='Signal time unit')

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
        showFilesPreviewDialog(
                        self.filesTableView.getSelectedPathAndFilename())

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
                                      [self.__signal_header_element__,
                                       self.__annotation_header_element__,
                                       self.__time_header_element__])
                self.__headerWidgets__.append(widget)
                # some value of global indicator have to be not None
                if not nvl(*self.__globalIndex__) == None:
                    widget.enabledAll(False)
                    if self.__globalIndex__.signal == num:  # signal index
                        widget.check(self.__signal_header_element__.name)
                    elif self.__globalIndex__.annotation == num:  # annotation index @IgnorePep8
                        widget.check(self.__annotation_header_element__.name)
                    if self.__globalIndex__.time == num:  # time index
                        widget.check(self.__time_header_element__.name)
                elif self.__signalColumnIndexes__.get(pathFile) == num:
                    widget.check(self.__signal_header_element__.name)
                elif self.__annotationColumnIndexes__.get(pathFile) == num:
                    widget.check(self.__annotation_header_element__.name)
                elif self.__timeColumnIndexes__.get(pathFile) == num:
                    widget.check(self.__time_header_element__.name)
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

        self.headersTablePreview = TableViewWidget(self.fileHeaderPreviewGroup,
                            selectionBehavior=QAbstractItemView.SelectRows,
                            selectionMode=QAbstractItemView.SingleSelection)

        self.__globalCheckBox__ = CheckBoxWidget(
                                    self.fileHeaderPreviewGroup,
                                    i18n="global.data.column.index",
                                    i18n_def="Global columns indexes",
                                    clicked_handler=self.__globalClicked__)
        if self.__globalIndex__.signal:
            self.__globalCheckBox__.setChecked(True)

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
            pathFile = self.filesTableView.getPathAndFilename(idx)
            if pathFile:
                self.__createDataFileHeader__(pathFile, _separator)

    def __signalWidgetHandler__(self, _widget):
        self.__widgetHandler__(_widget, self.__signal_header_element__.name)

    def __annotationWidgetHandler__(self, _widget):
        self.__widgetHandler__(_widget, self.__annotation_header_element__.name)  # @IgnorePep8

    def __timeWidgetHandler__(self, _widget):
        self.__widgetHandler__(_widget, self.__time_header_element__.name)

    def __widgetHandler__(self, _widget, _type):
        checked = _widget.isChecked(_type)
        pathFile = self.filesTableView.getSelectedPathAndFilename()
        if checked:
            for num, widget in enumerate(self.__headerWidgets__):
                if widget == _widget:
                    if _type == self.__signal_header_element__.name:
                        _widget.uncheck(self.__annotation_header_element__.name) # @IgnorePep8
                        self.__signalColumnIndexes__[pathFile] = num
                    elif _type == self.__annotation_header_element__.name:
                        _widget.uncheck(self.__signal_header_element__.name)
                        _widget.uncheck(self.__time_header_element__.name)
                        self.__annotationColumnIndexes__[pathFile] = num
                    elif _type == self.__time_header_element__.name:
                        _widget.uncheck(self.__annotation_header_element__.name) # @IgnorePep8
                        self.__timeColumnIndexes__[pathFile] = num
                else:
                    if _type == self.__signal_header_element__.name:
                        widget.uncheck(self.__signal_header_element__.name)
                    elif _type == self.__annotation_header_element__.name:
                        widget.uncheck(self.__annotation_header_element__.name)
                    elif _type == self.__time_header_element__.name:
                        widget.uncheck(self.__time_header_element__.name)

            self.__globalCheckBox__.setEnabled(True)
        else:
            if _type == self.__signal_header_element__.name:
                self.__signalColumnIndexes__[pathFile] = None
            elif _type == self.__annotation_header_element__.name:
                self.__annotationColumnIndexes__[pathFile] = None
            elif _type == self.__time_header_element__.name:
                self.__timeColumnIndexes__[pathFile] = None

    def __globalClicked__(self):

        _signal = None
        _annotation = None
        _time = None
        if self.__globalCheckBox__.isChecked():
            for num, widget in enumerate(self.__headerWidgets__):
                if widget.isChecked(self.__signal_header_element__.name):
                    _signal = num
                if widget.isChecked(self.__annotation_header_element__.name):
                    _annotation = num
                if widget.isChecked(self.__time_header_element__.name):
                    _time = num
            index = GlobalIndex(_signal, _annotation, _time)
            if index.signal == None:
                self.__globalCheckBox__.setChecked(False)
                InformationWindow(None,
                        message='At least signal column has to be selected !')
                return
            else:
                for num, widget in enumerate(self.__headerWidgets__):
                    widget.enabledAll(False)
                self.__globalIndex__ = index
                self.__setGlobalIndexForAll__(self.__globalIndex__)
        else:
            for widget in self.__headerWidgets__:
                widget.enabledAll(True)
            self.__globalIndex__ = GlobalIndex(None, None, None)

    def __setGlobalIndexForAll__(self, _globalIndex):
        model = self.filesTableView.model()
        for row in range(model.rowCount()):
            #it's necessity to alter model index of QSortFilterProxyModel type
            #into source model index of QStandardItemModel type
            idx = model.mapToSource(model.index(row, 0))
            pathFile = self.filesTableView.getPathAndFilename(idx)
            if pathFile:
                self.__signalColumnIndexes__[pathFile] = _globalIndex.signal

                if _globalIndex.annotation:  # annontation global index
                    self.__annotationColumnIndexes__[pathFile] = \
                                                    _globalIndex.annotation
                if _globalIndex.time:  # time global index
                    self.__timeColumnIndexes__[pathFile] = \
                                                    _globalIndex.time

    def __createHeaderPreviewGroup__(self):
        if hasattr(self, 'fileHeaderPreviewGroup'):
            self.fileHeaderPreviewGroup.deleteLater()
        self.fileHeaderPreviewGroup = GroupBoxWidget(self.tableViewComposite,
                                    i18n="datasource.file.header.preview",
                                    i18n_def="Header preview",
                                    layout=QVBoxLayout(),
                                    hidden=True,
                                    enabled=False)

    def validatePage(self):
        filesSpecificationModel = DatasourceFilesSpecificationModel()
        for (_path, _filename, _signalIndex, _annotationIndex, _timeIndex,
             _separator) in \
            self.__getFilesSpec__(indexes=True, separators=True):
                if _signalIndex == None:
                    ErrorWindow(message=("No signal column for the file %s !"
                                         % (_filename)))
                    return False
                if _separator == None:
                    ErrorWindow(message=("No separator for file %s !"
                                         % (_filename)))
                    return False
                filesSpecificationModel.appendRow(_path, _filename,
                    _signalIndex, _annotationIndex, _timeIndex, _separator,
                    self.__timeUnitsGroup__.getUnit())

        PluginsManager.invokePlugin(PluginsNames.TACHOGRAM_PLOT_PLUGIN_NAME,
                    inspect.stack(),
                    model=filesSpecificationModel.getAsFilesSpecifications(),
                    activity_description=self.__activity__.description(),
                    activity_params=['model'])
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
            pathFile = self.filesTableView.getPathAndFilename(idx)

            if pathFile:
                fileSpec = []
                if _pathfile == True:
                    fileSpec.extend(pathFile)

                if indexes == True:
                    signalIndex = self.__signalColumnIndexes__.get(pathFile)
                    if signalIndex == None and use_global_index == True and \
                        not self.__globalIndex__.signal == None:
                        signalIndex = self.__globalIndex__.signal
                    fileSpec.append(signalIndex)

                    annotationIndex = self.__annotationColumnIndexes__.get(
                                                                   pathFile)
                    if annotationIndex == None and use_global_index == True \
                        and not self.__globalIndex__.annotation == None:
                        annotationIndex = self.__globalIndex__.annotation
                    fileSpec.append(annotationIndex)

                    timeIndex = self.__timeColumnIndexes__.get(pathFile)
                    if timeIndex == None and use_global_index == True \
                        and not self.__globalIndex__.time == None:
                        timeIndex = self.__globalIndex__.time
                    fileSpec.append(timeIndex)

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


GlobalIndex = collections.namedtuple('GlobalIndex', ['signal', 'annotation', 'time']) # @IgnorePep8


class PreviewDataViewModel(QStandardItemModel):
    def __init__(self, parent):
        QStandardItemModel.__init__(self, parent=parent)

    def data(self, _modelIndex, _role):
        if _modelIndex.column() >= 0 and _role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        else:
            return super(PreviewDataViewModel, self).data(_modelIndex, _role)
