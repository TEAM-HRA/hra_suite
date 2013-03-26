'''
Created on 15-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import numpy as np
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas # @IgnorePep8
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar # @IgnorePep8
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.units import get_unit_by_class_name
    from pycore.units import OrderUnit
    from pycommon.actions import ActionSpec
    from pymath.datasources import FileDataSource
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.actions.actions_utils import create_action
    from pygui.qt.custom_widgets.filters import FiltersWidget
    from pygui.qt.plots.plots_signals import SHOW_TACHOGRAM_PLOT_SETTINGS
    from pygui.qt.plots.plots_signals import CHANGE_X_UNIT_TACHOGRAM_PLOT_SIGNAL # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotPlot(CompositeCommon):
    """
    this class represents core of the tachogram plot that is a plot itself
    """
    def __init__(self, parent, **params):
        super(TachogramPlotPlot, self).__init__(parent,
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
        self.navigation_toolbar = TachogramNavigationToolbar(self.canvas, self)
        layout.addWidget(self.navigation_toolbar)


class TachogramPlotCanvas(FigureCanvas):
    """
    this class represents core of the tachogram plot that is a plot itself
    """
    def __init__(self, parent, **params):
        #super(TachogramPlotCanvas, self).__init__(parent,
        #                                not_add_widget_to_parent_layout=True)
        self.params = Params(**params)
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        self.x_axis_unit = OrderUnit  # mark defualt x axis unit as order unit
        self.signal_unit = self.params.signal_unit
        self.calculate()
        FigureCanvas.__init__(self, self.fig)

        # automatic layout adjustment to use available space more efficiently
        self.fig.tight_layout()
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def calculate(self, _signal=None):
        if _signal == None:
            _signal = self.params.signal
        if self.x_axis_unit == OrderUnit:
            self.x = np.arange(0, len(_signal), 1)
        # x axis unit is the same as signal unit
        elif self.x_axis_unit == self.signal_unit:
            self.x = np.cumsum(_signal)
        else:
            #express signal unit in terms of x axis unit
            multiplier = self.signal_unit.expressInUnit(self.x_axis_unit)
            self.x = np.cumsum(_signal) * multiplier
        self.y = _signal


class TachogramNavigationToolbar(NavigationToolbar):

    def __init__(self, canvas, parent):
        # create the default toolbar
        NavigationToolbar.__init__(self, canvas, parent)
        self.canvas = canvas
        self.__current_plot__ = None
        # add new toolbar buttons

        normal_plot_action = self.__createAction__(title="Normal plot",
                                            handler=self.__normalPlot__,
                                            iconId='graph_button')
        self.addAction(normal_plot_action)

        scatter_plot_action = self.__createAction__(title="Scatter plot",
                                            handler=self.__scatterPlot__,
                                            iconId='scatter_plot_button')
        self.addAction(scatter_plot_action)

        tachogram_plot_settings_action = self.__createAction__(
                                        title="Tachogram plot settings",
                                        handler=self.__tachogramPlotSettings__,
                                        iconId='tachogram_plot_settings')
        self.addAction(tachogram_plot_settings_action)

        self.__normalPlot__()

        #add a filters combo box widget
        self.addWidget(FiltersWidget(parent,
                                     self.canvas.params.signal,
                                     self.canvas.params.annotation,
                                     clicked_handler=self.__filter_handler__))

        SignalDispatcher.addSignalSubscriber(self,
                                CHANGE_X_UNIT_TACHOGRAM_PLOT_SIGNAL,
                                self.__changeXUnit__)

    def __normalPlot__(self, force_plot=False):
        if self.__beforePlot__(self.__normalPlot__, force_plot):
            self.canvas.axes.plot(self.canvas.x, self.canvas.y)
            self.__afterPlot__()

    def __scatterPlot__(self, force_plot=False):
        if self.__beforePlot__(self.__scatterPlot__, force_plot):
            self.canvas.axes.plot(self.canvas.x, self.canvas.y, 'bo')
            self.__afterPlot__()

    def __createAction__(self, **params):
        return create_action(self.parent(), ActionSpec(**params))

    def __filter_handler__(self, _signal, _annotation):
        self._views.clear()  # clear all remembered view history
        self.canvas.calculate(_signal)
        self.__current_plot__(force_plot=True)

    def __tachogramPlotSettings__(self):
        SignalDispatcher.broadcastSignal(SHOW_TACHOGRAM_PLOT_SETTINGS,
                                         self.canvas.x_axis_unit)

    def __beforePlot__(self, _plot, force_plot):
        if force_plot == False and self.__current_plot__ == _plot:
            return False
        else:
            self.__current_plot__ = _plot
            self.canvas.axes.cla()
            return True

    def __afterPlot__(self):
        self.canvas.axes.set_xlabel(self.canvas.x_axis_unit.display_label)
        self.canvas.axes.set_ylabel(self.canvas.signal_unit.display_label)
        self.canvas.draw()

    def __changeXUnit__(self, _unit):
        self.canvas.x_axis_unit = _unit
        self.canvas.calculate()
        self.__current_plot__(force_plot=True)
