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
    from pygui.qt.utils.signals import TAB_WIDGET_ADDED_SIGNAL
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.utils.signals import ENABLEMEND_SIGNAL
    from pygui.qt.widgets.commons import maximize_widget
    from pygui.qt.widgets.commons import restore_widget
    from pygui.qt.widgets.splitter_widget import SplitterWidget
    from pygui.qt.custom_widgets.tabwidget import TabWidgetItemCommon
    from pygui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.tachogram_plot_manager import TachogramPlotManager
    from pygui.qt.plots.tachogram_plot_datasource_list_widget import TachogramPlotDatasourceListWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotTabWidget(TabWidgetItemCommon):

    def __init__(self, **params):
        super(TachogramPlotTabWidget, self).__init__(**params)
        self.params = Params(**params)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.__splitter__ = SplitterWidget(self, objectName='poincarePlot',
                                           save_state=True)
        self.__createDatasourceListWidget__()
        self.__createTachogramPlotManager__()

        #this method's call is very important, it sets up widgets sizes which
        #make up a splitter; it has to be the last operation in
        #the TachogramPlotTabWidget's creation process
        self.__splitter__.updateSizes()

    def beforeCloseTab(self):
        """
        this method includes actions to be invoked when a TachogramPlotTabWidget is closing @IgnorePep8
        """
        self.__splitter__.saveSettings()

    def __createDatasourceListWidget__(self):
        self.__datasourceListWidget__ = \
            TachogramPlotDatasourceListWidget(self.__splitter__,
                                              self.params.model,
                add_tachogram_plot_handler=self.__addTachogramPlot__,
                close_tachogram_plot_handler=self.closeTab,
                close_tachograms_handler=self.__closeTachogramsHandler__)
        if self.__splitter__.sizesLoaded() == False:
            idx = self.__splitter__.indexOf(self.__datasourceListWidget__)
            self.__splitter__.setStretchFactor(idx, 1)

    def __createTachogramPlotManager__(self):
        self.__tachogramsManager__ = TachogramPlotManager(self.__splitter__,
                                                     add_widget_to_parent=True)
        self.__initial_tachogram_plot__ = \
                        self.__tachogramsManager__.createInitialPlot()

        if self.__splitter__.sizesLoaded() == False:
            idx = self.__splitter__.indexOf(self.__tachogramsManager__)
            self.__splitter__.setStretchFactor(idx, 20)
        SignalDispatcher.addSignalSubscriber(self, CLOSE_TACHOGRAM_PLOT_SIGNAL,
                                            self.__closeTachogramPlot__)
        SignalDispatcher.addSignalSubscriber(self, TAB_WIDGET_ADDED_SIGNAL,
                                            self.__tachogramPlotAdded__)
        SignalDispatcher.addSignalSubscriber(self,
                                             MAXIMIZE_TACHOGRAM_PLOT_SIGNAL,
                                             self.__maximizeTachogramPlot__)
        SignalDispatcher.addSignalSubscriber(self,
                                             RESTORE_TACHOGRAM_PLOT_SIGNAL,
                                             self.__restoreTachogramPlot__)

    def __addTachogramPlot__(self, file_specification, allow_duplication,
                             first_focus):
        added = self.__tachogramsManager__.addTachogramPlot(
                                        file_specification,
                                        allow_duplication=allow_duplication,
                                        first_focus=first_focus)
        if added:
            self.__initial_tachogram_plot__.addFileSpecification(
                                                        file_specification)
        return added

    def __closeTachogramsHandler__(self):
        if AreYouSureWindow(self, title='Closing all tachograms plots'):
            self.__tachogramsManager__.closeAllTabs()
            return True
        return False

    def __tachogramPlotAdded__(self):
        self.__datasourceListWidget__.enabledCloseAllTachogramsButton(True)

    def __closeTachogramPlot__(self, _tachogram_plot_tab):
        """
        method invoked when tachogram plot is closed and then it checks
        there are any opened tachogram plots if this is not the case
        the button 'close all tachograms' is disabled
        """
        if self.__tachogramsManager__.countNotCloseTabs() == 0:
            self.__datasourceListWidget__.enabledCloseAllTachogramsButton(False) #  @IgnorePep8
            self.__datasourceListWidget__.emit(ENABLEMEND_SIGNAL, False)

    def __maximizeTachogramPlot__(self):
        maximize_widget(self.__tachogramsManager__)

    def __restoreTachogramPlot__(self):
        restore_widget(self.__tachogramsManager__)
