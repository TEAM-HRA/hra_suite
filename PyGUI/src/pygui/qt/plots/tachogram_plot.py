'''
Created on 15-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.utils.widgets import TabWidgetCommon
    from pygui.qt.utils.widgets import MainWindowCommon
    from pygui.qt.utils.widgets import LabelCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotManager(TabWidgetCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotManager, self).__init__(parent, **params)

    def addTachogramPlot(self):
        self.__createTachogramTab__("test")

    def createInitialPlot(self):
        self.__initial_tab__ = self.__createTachogramTab__('Welcome')
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label = LabelCommon(self.__initial_tab__,
                    i18n="tachogram.initial.page.label",
                    i18n_def="Tachogram area",
                    sizePolicy=sizePolicy,
                    not_add_widget_to_parent_layout=True)
        self.__initial_tab__.setCentralWidget(label)

    def __createTachogramTab__(self, _title=""):
        tachogramTabWidget = MainWindowCommon(self)  # , layout=QVBoxLayout())

#        toolbar = MaxMinToolBarWidget(self.__initial_tab__)
#        self.__initial_tab__.addToolBar(toolbar)
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
        #statusbar.addWidget(statusLabel)

        self.addTab(tachogramTabWidget, _title)
        return tachogramTabWidget
