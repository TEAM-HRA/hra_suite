'''
Created on 03-11-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import collections
    import inspect
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.collections_utils import create_list
    from pycore.collections_utils import nvl
    from pycore.io_utils import DataFileHeader
    from pygui.qt.activities.activities import ActivityWidget
    from pygui.qt.utils.windows import showFilesPreviewDialog
    from pygui.qt.utils.windows import InformationWindow
    from pygui.qt.utils.windows import ErrorWindow
    from pygui.qt.custom_widgets.modelviews import FilesTableView
    from pygui.qt.custom_widgets.modelviews import WidgetsHorizontalHeader
    from pygui.qt.custom_widgets.modelviews \
        import CheckStateProxySortFilterModel
    from pygui.qt.custom_widgets.global_separator_widget import GlobalSeparatorWidget # @IgnorePep8
    from pygui.qt.custom_widgets.units import TimeUnitsWidget
    from pygui.qt.models.datasources import DatasourceFilesSpecificationModel
    from pygui.qt.utils.plugins import PluginsManager
    from pygui.qt.utils.plugins import PluginsNames
    from pygui.qt.widgets.label_widget import LabelWidget
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
    from pygui.qt.widgets.table_view_widget import TableViewWidget
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
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
        self.__globalIndex__ = ColumnType(None, None, None)

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
                                      self.__signalWidgetHandler__,
                                      self.__annotationWidgetHandler__,
                                      self.__timeWidgetHandler__)
                self.__headerWidgets__.append(widget)
                # some value of global indicator have to be not None
                if not nvl(*self.__globalIndex__) == None:
                    widget.enabledAll(False)
                    if self.__globalIndex__.signal == num:  # signal index
                        widget.check(ColumnType.signal)
                    elif self.__globalIndex__.annotation == num:  # annotation index @IgnorePep8
                        widget.check(ColumnType.annotation)
                    if self.__globalIndex__.time == num:  # time index
                        widget.check(ColumnType.time)
                elif self.__signalColumnIndexes__.get(pathFile) == num:
                    widget.check(ColumnType.signal)
                elif self.__annotationColumnIndexes__.get(pathFile) == num:
                    widget.check(ColumnType.annotation)
                elif self.__timeColumnIndexes__.get(pathFile) == num:
                    widget.check(ColumnType.time)
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
        self.__widgetHandler__(_widget, ColumnType.signal)

    def __annotationWidgetHandler__(self, _widget):
        self.__widgetHandler__(_widget, ColumnType.annotation)

    def __timeWidgetHandler__(self, _widget):
        self.__widgetHandler__(_widget, ColumnType.time)

    def __widgetHandler__(self, _widget, _type):
        checked = _widget.isChecked(_type)
        pathFile = self.filesTableView.getSelectedPathAndFilename()
        if checked:
            for num, widget in enumerate(self.__headerWidgets__):
                if widget == _widget:
                    if _type == ColumnType.signal:
                        _widget.uncheck(ColumnType.annotation)
                        self.__signalColumnIndexes__[pathFile] = num
                    elif _type == ColumnType.annotation:
                        _widget.uncheck(ColumnType.signal)
                        _widget.uncheck(ColumnType.time)
                        self.__annotationColumnIndexes__[pathFile] = num
                    elif _type == ColumnType.time:
                        _widget.uncheck(ColumnType.annotation)
                        self.__timeColumnIndexes__[pathFile] = num
                else:
                    if _type == ColumnType.signal:
                        widget.uncheck(ColumnType.signal)
                    elif _type == ColumnType.annotation:
                        widget.uncheck(ColumnType.annotation)
                    elif _type == ColumnType.time:
                        widget.uncheck(ColumnType.time)

            self.__globalCheckBox__.setEnabled(True)
        else:
            if _type == ColumnType.signal:
                self.__signalColumnIndexes__[pathFile] = None
            elif _type == ColumnType.annotation:
                self.__annotationColumnIndexes__[pathFile] = None
            elif _type == ColumnType.time:
                self.__timeColumnIndexes__[pathFile] = None

    def __globalClicked__(self):

        _signal = None
        _annotation = None
        _time = None
        if self.__globalCheckBox__.isChecked():
            for num, widget in enumerate(self.__headerWidgets__):
                if widget.isChecked(ColumnType.signal):
                    _signal = num
                if widget.isChecked(ColumnType.annotation):
                    _annotation = num
                if widget.isChecked(ColumnType.time):
                    _time = num
            index = ColumnType(_signal, _annotation, _time)
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
            self.__globalIndex__ = ColumnType(None, None, None)

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

ColumnType = collections.namedtuple('ColumnType', ['signal', 'annotation', 'time']) # @IgnorePep8


class HeaderWidget(QWidget):

    def __init__(self, _parent, _header,
                 _dataHandler, _annotationHandler, _timeHandler):
        QWidget.__init__(self, parent=_parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        LabelWidget(self, i18n_def=_header)

        self.__buttons__ = {}
        self.__buttons__[ColumnType.signal] = CheckBoxWidget(self,
                                    i18n_def="signal",
                                    clicked_handler=self.__signalClicked__)
        self.__buttons__[ColumnType.annotation] = CheckBoxWidget(self,
                                    i18n_def="annotation",
                                    clicked_handler=self.__annotationClicked__)
        self.__buttons__[ColumnType.time] = CheckBoxWidget(self,
                                    i18n_def="time",
                                    clicked_handler=self.__timeClicked__)

        self.__dataHandler__ = _dataHandler
        self.__annotationHandler__ = _annotationHandler
        self.__timeHandler__ = _timeHandler

    def __annotationClicked__(self):
        self.__annotationHandler__(self)

    def __signalClicked__(self):
        self.__dataHandler__(self)

    def __timeClicked__(self):
        self.__timeHandler__(self)

    def check(self, _type):
        self.__getButton__(_type).setChecked(True)

    def uncheck(self, _type):
        self.__getButton__(_type).setChecked(False)

    def isChecked(self, _type):
        return self.__getButton__(_type).isChecked()

    def enabled(self, _type, _enabled):
        self.__getButton__(_type).setEnabled(_enabled)

    def enabledAll(self, _enabled):
        self.enabled(ColumnType.signal, _enabled)
        self.enabled(ColumnType.annotation, _enabled)
        self.enabled(ColumnType.time, _enabled)

    def __getButton__(self, _type):
        return self.__buttons__[_type]

    def buttons(self):
        return self.__buttons__


class PreviewDataViewModel(QStandardItemModel):
    def __init__(self, parent):
        QStandardItemModel.__init__(self, parent=parent)

    def data(self, _modelIndex, _role):
        if _modelIndex.column() >= 0 and _role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        else:
            return super(PreviewDataViewModel, self).data(_modelIndex, _role)
