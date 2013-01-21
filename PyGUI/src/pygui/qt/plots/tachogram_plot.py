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
    from pygui.qt.utils.widgets import WidgetCommon
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.custom_widgets.tabwidget import TabWidgetCallableCloseHandler
    from pygui.qt.custom_widgets.tabwidget import TabWidgetCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotManager(TabWidgetCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotManager, self).__init__(parent, **params)

    def addTachogramPlots(self, files_specifications, allow_duplication=False):
        first = True
        count_opened = 0
        for file_specification in files_specifications:
            object_name = self.__getObjectName__(file_specification)
            if allow_duplication == False and self.tabExists(object_name):
                continue
            tab = self.__createTachogramTab__(file_specification, object_name)
            if first:
                first = False
                self.setTabFocus(tab)
            if tab:
                count_opened = count_opened + 1
        return count_opened

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

    def __createTachogramTab__(self, file_specification, object_name):
        tachogramTabWidget = TachogramPlotWindow(self,
                                    file_specification=file_specification)
        tachogramTabWidget.setObjectName(object_name)
        self.addTab(tachogramTabWidget,
                    self.getNextTitle(file_specification.filename))
        return tachogramTabWidget

    def __getObjectName__(self, file_specification):
        return ".".join([file_specification.filepath,
                         file_specification.filename])


class TachogramPlotWindow(MainWindowCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotWindow, self).__init__(parent, **params)
        self.params = Params(**params)
        close_handler = TabWidgetCallableCloseHandler(parent, self)
        self.addToolBar(OperationalToolBarWidget(self,
                             toolbar_close_handler_callable=close_handler))

        self.tachogramPlot = TachogramPlotPlot(self)
        self.setCentralWidget(self.tachogramPlot)
#        statusbar = StatusBarCommon(self.__initial_tab__)
#        self.__initial_tab__.setStatusBar(statusbar)
#        statusLabel = LabelCommon(statusbar,
#                    i18n_def="STATUS",
#                    add_widget_to_parent=True)
#
#        logDockWidget = QDockWidget("Log", self.__initial_tab__)
#        logDockWidget.setObjectName("LogDockWidget")
#        logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |
#                                      Qt.RightDockWidgetArea)
#        self.listWidget = QListWidget()
#        logDockWidget.setWidget(self.listWidget)
#        self.__initial_tab__.addDockWidget(Qt.RightDockWidgetArea,
#                                           logDockWidget)


class TachogramPlotPlot(WidgetCommon):
    """
    this class represents core of the tachogram plot that is a plot itself
    """
    def __init__(self, parent, **params):
        super(TachogramPlotPlot, self).__init__(parent,
                                        not_add_widget_to_parent_layout=True)
