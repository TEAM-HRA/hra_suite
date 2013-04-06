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
    from pycore.units import get_unit_by_class_name
    from pymath.datasources import FileDataSource
    from pygui.qt.utils.widgets import MainWindowCommon
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.tachogram_plot_settings_dock_widget import TachogramPlotSettingsDockWidget # @IgnorePep8
    from pygui.qt.plots.tachogram_plot_statistics_dock_widget import TachogramPlotStatisticsDockWidget  # @IgnorePep8
    from pygui.qt.plots.tachogram_plot_canvas import TachogramPlotCanvas
    from pygui.qt.plots.tachogram_plot_navigator_toolbar import TachogramPlotNavigationToolbar  # @IgnorePep8    
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotWindow(MainWindowCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotWindow, self).__init__(parent, **params)
        self.params = Params(**params)

        self.addToolBar(OperationalToolBarWidget(self))

        self.tachogramPlot = TachogramPlot(self,
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


class TachogramPlot(CompositeCommon):
    """
    this class represents core of the tachogram plot that is a plot itself
    """
    def __init__(self, parent, **params):
        super(TachogramPlot, self).__init__(parent,
                                        not_add_widget_to_parent_layout=True)
        self.params = Params(**params)
        file_data_source_params = self.params.file_specification._asdict()
        self.signal_unit = get_unit_by_class_name(
                        file_data_source_params.get('signal_unit_class_name'))
        file_data_source = FileDataSource(**file_data_source_params)
        data = file_data_source.getData()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.canvas = TachogramPlotCanvas(self, signal=data.signal,
                                          annotation=data.annotation,
                                          signal_unit=data.signal_unit)
        layout.addWidget(self.canvas)
        self.navigation_toolbar = TachogramPlotNavigationToolbar(self.canvas,
                            self,
                            show_tachogram_plot_settings_handler=self.params.show_tachogram_plot_settings_handler, # @IgnorePep8
                            show_tachogram_plot_statistics_handler=self.params.show_tachogram_plot_statistics_handler) # @IgnorePep8
        layout.addWidget(self.navigation_toolbar)

    def changeXUnit(self, _unit):
        self.canvas.changeXUnit(_unit)
