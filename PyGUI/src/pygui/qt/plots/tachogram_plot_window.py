'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.introspection import get_child_of_type
    from pygui.qt.utils.widgets import MainWindowCommon
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.plots.tachogram_plot_plot import TachogramPlotPlot
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.tachogram_plot_settings_dock_widget import TachogramPlotSettingsDockWidget # @IgnorePep8
    from pygui.qt.plots.tachogram_plot_statistics_dock_widget import TachogramPlotStatisticsDockWidget  # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotWindow(MainWindowCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotWindow, self).__init__(parent, **params)
        self.params = Params(**params)

        self.addToolBar(OperationalToolBarWidget(self))

        self.tachogramPlot = TachogramPlotPlot(self,
            file_specification=self.params.file_specification,
            show_tachogram_plot_settings_handler=self.__show_tachogram_plot_settings_handler__,   # @IgnorePep8
            show_tachogram_plot_statistics_handler=self.__show_tachogram_plot_statistics_handler__)  # @IgnorePep8
        self.setCentralWidget(self.tachogramPlot)

    def toolbar_maximum_handler(self):
        SignalDispatcher.broadcastSignal(MAXIMIZE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_restore_handler(self):
        SignalDispatcher.broadcastSignal(RESTORE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_close_handler(self):
        SignalDispatcher.broadcastSignal(CLOSE_TACHOGRAM_PLOT_SIGNAL, self)

    def __show_tachogram_plot_settings_handler__(self, _x_unit):
        tachogram_plot_dock_widget = get_child_of_type(self,
                                             TachogramPlotSettingsDockWidget)
        if tachogram_plot_dock_widget == None:
            tachogram_plot_dock_widget = TachogramPlotSettingsDockWidget(self,
                            x_unit=_x_unit,
                            change_unit_handler=self.__change_unit_handler__)
        tachogram_plot_dock_widget.show()

    def __show_tachogram_plot_statistics_handler__(self):
        dock_widget = get_child_of_type(self, TachogramPlotStatisticsDockWidget) # @IgnorePep8
        if dock_widget == None:
            dock_widget = TachogramPlotStatisticsDockWidget(self,
                            file_specification=self.params.file_specification)
        dock_widget.show()

    def __change_unit_handler__(self, _unit):
        self.tachogramPlot.changeXUnit(_unit)
#        statusbar = StatusBarCommon(self.__initial_tab__)
#        self.__initial_tab__.setStatusBar(statusbar)
#        statusLabel = LabelCommon(statusbar,
#                    i18n_def="STATUS",
#                    add_widget_to_parent=True)
#
