'''
Created on 05-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.windows import AreYouSureWindow
    from pygui.qt.utils.windows import showFilesPreviewDialog
    from pygui.qt.utils.widgets import PushButtonCommon
    from pygui.qt.utils.widgets import WidgetCommon
    from pygui.qt.utils.widgets import ListWidgetCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.signals import TAB_WIDGET_CLOSE_SIGNAL
    from pygui.qt.utils.signals import TAB_WIDGET_ADDED_SIGNAL
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.utils.widgets import ListWidgetItemCommon
    from pygui.qt.custom_widgets.splitter import SplitterWidget
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.custom_widgets.toolbars import ToolBarManager
    from pygui.qt.custom_widgets.toolbars import CheckUncheckToolBarWidget
    from pygui.qt.custom_widgets.tabwidget import TabWidgetItemCommon
    from pygui.qt.custom_widgets.progress_bar import ProgressDialogManager
    from pygui.qt.utils.signals import ENABLEMEND_SIGNAL
    from pygui.qt.plots.tachogram_plot import TachogramPlotManager
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PoincarePlotTabWidget(TabWidgetItemCommon):

    def __init__(self, **params):
        super(PoincarePlotTabWidget, self).__init__(**params)
        self.params = Params(**params)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.__splitter__ = SplitterWidget(self, objectName='poincarePlot',
                                           save_state=True)
        self.__createDatasourceListWidget__()
        self.__createTachogramPlotManager__()

        #this method's call is very important, it sets up widgets sizes which
        #make up a splitter; it has to be the last operation in
        #the PoincarePlotTabWidget's creation process
        self.__splitter__.updateSizes()

    def beforeCloseTab(self):
        """
        this method includes actions to be invoked when a PoincarePlotTabWidget is closing @IgnorePep8
        """
        self.__splitter__.saveSettings()

    def __createDatasourceListWidget__(self):
        self.__datasourceListWidget__ = \
            DatasourceListWidget(self.__splitter__, self.params.model,
                add_tachogram_plot_handler=self.__addTachogramPlot__,
                close_tachogram_plot_handler=self.closeTab,
                close_tachograms_handler=self.__closeTachogramsHandler__)
        if self.__splitter__.sizesLoaded() == False:
            idx = self.__splitter__.indexOf(self.__datasourceListWidget__)
            self.__splitter__.setStretchFactor(idx, 1)

    def __createTachogramPlotManager__(self):
        self.__tachogramsManager__ = TachogramPlotManager(self.__splitter__,
                                                     add_widget_to_parent=True)
        self.__tachogramsManager__.createInitialPlot()
        if self.__splitter__.sizesLoaded() == False:
            idx = self.__splitter__.indexOf(self.__tachogramsManager__)
            self.__splitter__.setStretchFactor(idx, 20)
        SignalDispatcher.addSignalSubscriber(self, TAB_WIDGET_CLOSE_SIGNAL,
                                            self.__closeTachogramPlot__)
        SignalDispatcher.addSignalSubscriber(self, TAB_WIDGET_ADDED_SIGNAL,
                                            self.__tachogramPlotAdded__)

    def __addTachogramPlot__(self, files_specifications, allow_duplication,
                             first_focus):
        return self.__tachogramsManager__.addTachogramPlot(
                                        files_specifications,
                                        allow_duplication=allow_duplication,
                                        first_focus=first_focus)

    def __closeTachogramsHandler__(self):
        if AreYouSureWindow(self, title='Closing all tachograms plots'):
            self.__tachogramsManager__.closeAllTabs()
            return True
        return False

    def __tachogramPlotAdded__(self):
        self.__datasourceListWidget__.enabledCloseAllTachogramsButton(True)

    def __closeTachogramPlot__(self):
        """
        method invoked when tachogram plot is closed and then it checks
        there are any opened tachogram plots if this is not the case
        the button 'close all tachograms' is disabled
        """
        if self.__tachogramsManager__.countNotCloseTabs() == 0:
            self.__datasourceListWidget__.enabledCloseAllTachogramsButton(False) #  @IgnorePep8
            self.__datasourceListWidget__.emit(ENABLEMEND_SIGNAL, False)


class DatasourceListWidget(WidgetCommon):
    def __init__(self, parent, model, **params):
        super(DatasourceListWidget, self).__init__(parent,
                                                    add_widget_to_parent=True,
                                                    layout=QVBoxLayout())
        self.params = Params(**params)
        toolbars = ToolBarManager(self, CheckUncheckToolBarWidget,
                OperationalToolBarWidget,
                toolbar_close_handler=self.params.close_tachogram_plot_handler)
        self.layout().addWidget(toolbars)

        self.__filesPreviewButton__ = PushButtonCommon(self,
                    i18n="poincare.plot.files.preview.button",
                    i18n_def="Files preview",
                    enabled=False,
                    clicked_handler=self.__filesPreviewHandler__,
                    enabled_precheck_handler=self.__enabledPrecheckHandler__)

        self.__datasourceList__ = \
            ListWidgetCommon(self,
                list_item_clicked_handler=self.__datasourceItemClickedHandler__, # @IgnorePep8
                list_item_double_clicked_handler=self.__datasourceDoubleItemClickedHandler__, # @IgnorePep8
                selectionMode=QAbstractItemView.MultiSelection,
                selectionBehavior=QAbstractItemView.SelectRows)
        if len(model) > 0:
            for row in range(len(model)):
                fileSpecification = model[row]
                ListWidgetItemCommon(self.__datasourceList__,
                                     text=fileSpecification.filename,
                                     data=fileSpecification)
        else:
            ListWidgetItemCommon(self.__datasourceList__,
                                 text='model not specified or incorrect type')
        self.__showTachogramsButton__ = PushButtonCommon(self,
                    i18n="poincare.plot.show.tachograms.button",
                    i18n_def="Show tachograms",
                    enabled=False,
                    clicked_handler=self.__showTachogramsHandler__,
                    enabled_precheck_handler=self.__enabledPrecheckHandler__)

        self.__allowTachogramsDuplicationButton__ = CheckBoxCommon(self,
                    i18n="poincare.plot.allow.tachograms.duplications.button",
                    i18n_def="Allow tachograms duplication",
                    enabled=False,
                    enabled_precheck_handler=self.__enabledPrecheckHandler__)

        self.__closeAllTachogramsButton__ = PushButtonCommon(self,
                    i18n="poincare.plot.close.all.tachograms.button",
                    i18n_def="Close all tachograms",
                    enabled=False,
                    clicked_handler=self.__closeTachogramsHandler__)

    def __datasourceItemClickedHandler__(self, listItem):
        self.emit(ENABLEMEND_SIGNAL, listItem.isSelected())

    def __showTachogramsHandler__(self):
        self.__showTachograms__(self.__getFilesSpecifications__(selected=True))

    def __filesPreviewHandler__(self):
        showFilesPreviewDialog(self.__getFilesSpecifications__(selected=True))

    def __datasourceDoubleItemClickedHandler__(self, listItem):
        self.__showTachograms__(self.__getFilesSpecifications__([listItem]))

    def __showTachograms__(self, files_specifications):
        progressManager = ProgressDialogManager(self,
                                        label_text="Create tachograms",
                                        max_value=len(files_specifications))
        firstFocus = True
        checked = self.__allowTachogramsDuplicationButton__.isChecked()
        with progressManager as progress:
            for idx in range(progress.maximum()):
                if (progress.wasCanceled()):
                    break
                progress.increaseCounter()
                tachogram_plot = self.params.add_tachogram_plot_handler(
                                            files_specifications[idx],
                                            checked, firstFocus)
                if firstFocus and tachogram_plot:
                    firstFocus = False

        self.__datasourceList__.clearSelection()

    def __enabledPrecheckHandler__(self, widget):
        """
        only interested widgets return bool value others return none value
        """
        if widget in (self.__showTachogramsButton__,
                      self.__allowTachogramsDuplicationButton__,
                      self.__filesPreviewButton__):
            return len(self.__datasourceList__.selectedIndexes()) > 0

    def __closeTachogramsHandler__(self):
        if self.params.close_tachograms_handler:
            if self.params.close_tachograms_handler():
                self.__closeAllTachogramsButton__.setEnabled(False)
        self.toolbar_uncheck_handler()

    def toolbar_uncheck_handler(self):
        self.__datasourceList__.clearSelection()
        self.emit(ENABLEMEND_SIGNAL, False)

    def toolbar_check_handler(self):
        self.__datasourceList__.selectAll()
        self.emit(ENABLEMEND_SIGNAL, True)

    def enabledCloseAllTachogramsButton(self, enabled):
        self.__closeAllTachogramsButton__.setEnabled(enabled)

    def __getFilesSpecifications__(self, list_items=None, selected=False):
        if selected:  # get files specifications from selected items
            list_items = self.__datasourceList__.selectedItems()
        #acquired from data buffer of list items file specification objects
        return [list_item.getData() for list_item in list_items]
