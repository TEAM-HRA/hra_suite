'''
Created on 15-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.widgets import MainWindowCommon
    from pygui.qt.utils.widgets import LabelCommon
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.custom_widgets.tabwidget import TabWidgetCommon
    from pygui.qt.plots.tachogram_plot_plot import TachogramPlotPlot
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.utils.signals import TAB_WIDGET_ADDED_SIGNAL
except ImportError as error:
    ImportErrorMessage(error, __name__)

#signal emitted to maximize tachogram plot
MAXIMIZE_TACHOGRAM_PLOT_SIGNAL = SIGNAL('maximize_tachogram_plot()')
#signal emitted to restore tachogram plot
RESTORE_TACHOGRAM_PLOT_SIGNAL = SIGNAL('restore_tachogram_plot()')
#signal emitted to close tachogram plot
CLOSE_TACHOGRAM_PLOT_SIGNAL = SIGNAL('close_tachogram_plot(PyQt_PyObject)')


class TachogramPlotManager(TabWidgetCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotManager, self).__init__(parent, **params)
        SignalDispatcher.addSignalSubscriber(self,
                                             CLOSE_TACHOGRAM_PLOT_SIGNAL,
                                             self.__closeTachogramPlotTab__)

    def addTachogramPlot(self, file_specification, allow_duplication=False,
                         first_focus=False):
        if file_specification:
            object_name = self.__getObjectName__(file_specification)
            if allow_duplication == False and self.tabExists(object_name):
                return
            tab = self.__createTachogramTab__(file_specification, object_name)
            if tab and first_focus:
                self.setTabFocus(tab)
            return tab

    def createInitialPlot(self):
        self.__initial_tab__ = MainWindowCommon(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label = LabelCommon(self.__initial_tab__,
                            i18n="tachogram.initial.page.label",
                            i18n_def="Tachogram area",
                            sizePolicy=sizePolicy,
                            not_add_widget_to_parent_layout=True)
        self.__initial_tab__.setCentralWidget(label)
        self.addTab(self.__initial_tab__, 'Welcome')
        self.markTabAsNotClose(self.__initial_tab__)

    def __createTachogramTab__(self, file_specification, object_name):
        tachogramTabWidget = TachogramPlotWindow(self,
                                    file_specification=file_specification)
        tachogramTabWidget.setObjectName(object_name)
        self.addTab(tachogramTabWidget,
                    self.getNextTitle(file_specification.filename))
        SignalDispatcher.broadcastSignal(TAB_WIDGET_ADDED_SIGNAL)
        return tachogramTabWidget

    def __getObjectName__(self, file_specification):
        return ".".join([file_specification.pathname,
                         file_specification.filename])

    def __closeTachogramPlotTab__(self, _tachogram_plot_tab):
        idx = self.indexOf(_tachogram_plot_tab)
        self.removeTab(idx)


class TachogramPlotWindow(MainWindowCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotWindow, self).__init__(parent, **params)
        self.params = Params(**params)

        self.addToolBar(OperationalToolBarWidget(self))

        self.tachogramPlot = TachogramPlotPlot(self,
                        file_specification=self.params.file_specification)
        self.setCentralWidget(self.tachogramPlot)

    def toolbar_maximum_handler(self):
        SignalDispatcher.broadcastSignal(MAXIMIZE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_restore_handler(self):
        SignalDispatcher.broadcastSignal(RESTORE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_close_handler(self):
        SignalDispatcher.broadcastSignal(CLOSE_TACHOGRAM_PLOT_SIGNAL, self)
#        statusbar = StatusBarCommon(self.__initial_tab__)
#        self.__initial_tab__.setStatusBar(statusbar)
#        statusLabel = LabelCommon(statusbar,
#                    i18n_def="STATUS",
#                    add_widget_to_parent=True)
#
