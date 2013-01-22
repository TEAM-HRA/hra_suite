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
    from pygui.qt.utils.widgets import PushButtonCommon
    from pygui.qt.utils.widgets import WidgetCommon
    from pygui.qt.utils.widgets import ListWidgetCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.signals import TAB_WIDGET_CLOSE_SIGNAL
    from pygui.qt.models.datasources import DatasourceFilesSpecificationModel
    from pygui.qt.custom_widgets.splitter import SplitterWidget
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.custom_widgets.toolbars import ToolBarManager
    from pygui.qt.custom_widgets.toolbars import CheckUncheckToolBarWidget
    from pygui.qt.custom_widgets.tabwidget import TabWidgetItemCommon
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
                add_tachogram_plots_handler=self.__addTachogramPlots__,
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
        self.connect(self.__tachogramsManager__, TAB_WIDGET_CLOSE_SIGNAL,
                     self.__closeTachogramPlot__)

    def __addTachogramPlots__(self, files_specifications, allow_duplication):
        return self.__tachogramsManager__.addTachogramPlots(
                                        files_specifications,
                                        allow_duplication=allow_duplication)

    def __closeTachogramsHandler__(self):
        if AreYouSureWindow(self, title='Closing all tachograms plots'):
            self.__tachogramsManager__.closeAllTabs()
            return True
        return False

    def __closeTachogramPlot__(self):
        """
        method invoked when tachogram plot is closed and then it checks
        there are any opened tachogram plots if this is not the case
        the button 'close all tachograms' is disabled
        """
        if self.__tachogramsManager__.countNotCloseTabs() == 0:
            self.__datasourceListWidget__.enabledCloseAllTachogramsButton(False) #  @IgnorePep8


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

        self.__datasourceList__ = \
            ListWidgetCommon(self,
                list_item_clicked_handler=self.__datasourceItemClickedHandler__, # @IgnorePep8
                selectionMode=QAbstractItemView.MultiSelection,
                selectionBehavior=QAbstractItemView.SelectRows)
        if model and \
            isinstance(model, DatasourceFilesSpecificationModel):
            for row in range(model.rowCount()):
                fileSpecification = model.fileSpecification(row)
                listItem = QListWidgetItem(fileSpecification.filename,
                                           self.__datasourceList__)
                #store in data buffer of list item the whole file
                #specification object for later use
                listItem.setData(Qt.UserRole, QVariant(fileSpecification))
        else:
            QListWidgetItem('model not specified or incorrect type',
                            self.__datasourceList__)
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
        if self.params.add_tachogram_plots_handler:
            #acquired from data buffer of list items file specification objects
            files_specifications = [listItem.data(Qt.UserRole).toPyObject()
                    for listItem in self.__datasourceList__.selectedItems()]

            if self.params.add_tachogram_plots_handler(files_specifications,
                    self.__allowTachogramsDuplicationButton__.isChecked()) > 0:
                #if some tachograms plots are successfully opened
                self.__closeAllTachogramsButton__.setEnabled(True)

    def __enabledPrecheckHandler__(self, widget):
        """
        only interested widgets return bool value others return none value
        """
        if widget in (self.__showTachogramsButton__,
                      self.__allowTachogramsDuplicationButton__):
            return len(self.__datasourceList__.selectedIndexes()) > 0

    def __closeTachogramsHandler__(self):
        if self.params.close_tachograms_handler:
            if self.params.close_tachograms_handler():
                self.__closeAllTachogramsButton__.setEnabled(False)

    def toolbar_uncheck_handler(self):
        self.__datasourceList__.clearSelection()
        self.emit(ENABLEMEND_SIGNAL, False)

    def toolbar_check_handler(self):
        self.__datasourceList__.selectAll()
        self.emit(ENABLEMEND_SIGNAL, True)

    def enabledCloseAllTachogramsButton(self, enabled):
        self.__closeAllTachogramsButton__.setEnabled(enabled)
