'''
Created on 15-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.widgets import TabWidgetCommon
    from pygui.qt.utils.widgets import MainWindowCommon
    from pygui.qt.utils.widgets import LabelCommon
    from pygui.qt.utils.widgets import TabWidgetCallableCloseHandler
    from pygui.qt.utils.toolbars import OperationalToolBarWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotManager(TabWidgetCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotManager, self).__init__(parent, **params)

    def addTachogramPlot(self, file_specification, allow_duplication=False):
        if not allow_duplication and \
            self.tabExists(self.__getObjectName__(file_specification)):
            return
        self.__createTachogramTab__(file_specification)

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

    def __createTachogramTab__(self, file_specification):
        tachogramTabWidget = TachogramPlotWindow(self,
                                    file_specification=file_specification)
        tachogramTabWidget.setObjectName(
                                    self.__getObjectName__(file_specification))
        self.addTab(tachogramTabWidget, file_specification.filename)
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
