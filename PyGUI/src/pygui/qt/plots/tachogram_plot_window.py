'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.units import get_unit_by_class_name
    from pycore.units import OrderUnit
    from pymath.datasources import FileDataSource
    from pymath.datasources import DataVectorAccessor
    from pygui.qt.utils.widgets import MainWindowCommon
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.tachogram_plot_canvas import TachogramPlotCanvas
    from pygui.qt.plots.tachogram_plot_navigator_toolbar import TachogramPlotNavigationToolbar  # @IgnorePep8    
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotWindow(MainWindowCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotWindow, self).__init__(parent, **params)
        self.params = Params(**params)

        self.addToolBar(OperationalToolBarWidget(self))

        self.tachogramPlot = __TachogramPlot__(self,
                            file_specification=self.params.file_specification)
        self.setCentralWidget(self.tachogramPlot)

    def toolbar_maximum_handler(self):
        SignalDispatcher.broadcastSignal(MAXIMIZE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_restore_handler(self):
        SignalDispatcher.broadcastSignal(RESTORE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_close_handler(self):
        SignalDispatcher.broadcastSignal(CLOSE_TACHOGRAM_PLOT_SIGNAL, self)

#    def __change_unit_handler__(self, _unit):
#        self.tachogramPlot.changeXUnit(_unit)
#        statusbar = StatusBarCommon(self.__initial_tab__)
#        self.__initial_tab__.setStatusBar(statusbar)
#        statusLabel = LabelWidget(statusbar,
#                    i18n_def="STATUS",
#                    add_widget_to_parent=True)
#


class __TachogramPlot__(CompositeWidget):
    """
    this class represents core of the tachogram plot that is a plot itself
    """
    def __init__(self, parent, **params):
        super(__TachogramPlot__, self).__init__(parent,
                                        not_add_widget_to_parent_layout=True)
        self.params = Params(**params)
        file_data_source_params = self.params.file_specification._asdict()
        self.signal_unit = get_unit_by_class_name(
                        file_data_source_params.get('signal_unit_class_name'))
        file_data_source = FileDataSource(**file_data_source_params)
        layout = QVBoxLayout()
        self.setLayout(layout)
        data = file_data_source.getData()
        data_accessor = DataVectorAccessor(data)
        data_accessor.changeXSignalUnit(self, OrderUnit)
        self.canvas = TachogramPlotCanvas(self, data_accessor=data_accessor)
        layout.addWidget(self.canvas)
        self.navigation_toolbar = TachogramPlotNavigationToolbar(
                                                self, self.canvas,
                                                dock_parent=parent,
                                                data_accessor=data_accessor)
        layout.addWidget(self.navigation_toolbar)
