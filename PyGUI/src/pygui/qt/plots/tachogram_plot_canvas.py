'''
Created on 06-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import numpy as np
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas # @IgnorePep8
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.units import OrderUnit
    from pycore.collections_utils import nvl
    from pygui.qt.utils.dnd import CopyDropper
    from pygui.qt.plots.tachogram_plot_const import STATISTIC_MIME_ID
    from pygui.qt.plots.tachogram_plot_const import STATISTIC_CLASS_NAME_ID
except ImportError as error:
    ImportErrorMessage(error, __name__)


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
        self.y = self.params.signal
        self.__current_plot__ = None
        self.__current_plot_handler__ = None
        self.calculate()
        FigureCanvas.__init__(self, self.fig)

        # automatic layout adjustment to use available space more efficiently
        self.fig.tight_layout()
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.__dropper__ = CopyDropper(self, STATISTIC_MIME_ID)

    def calculate(self, _signal=None, _x_axis_unit=None):
        self.y = nvl(_signal, self.y)
        self.x_axis_unit = nvl(_x_axis_unit, self.x_axis_unit)
        if self.x_axis_unit == OrderUnit:
            self.x = np.arange(0, len(self.y), 1)
        # x axis unit is the same as signal unit
        elif self.x_axis_unit == self.signal_unit:
            self.x = np.cumsum(self.y)
        else:
            #express signal unit in terms of x axis unit
            multiplier = self.signal_unit.expressInUnit(self.x_axis_unit)
            self.x = np.cumsum(self.y) * multiplier

    def changeXUnit(self, _unit):
        self.plot(force_plot=True, _x_axis_unit=_unit)

    def plot(self, _plot_handler=None, force_plot=False, _signal=None,
             _x_axis_unit=None):
        if _plot_handler == None:
            _plot_handler = self.__current_plot_handler__
        if force_plot == False and \
            self.__current_plot_handler__ == _plot_handler:
            return
        else:
            self.__current_plot_handler__ = _plot_handler
            self.axes.cla()

        if not _signal == None or not _x_axis_unit == None:
            self.calculate(_signal=_signal, _x_axis_unit=_x_axis_unit)

        _plot_handler(self)

        self.axes.set_xlabel(self.x_axis_unit.display_label)
        self.axes.set_ylabel(self.signal_unit.display_label)
        self.draw()

    def dropEvent(self, event):
        if self.__dropper__.dropEvent(event):
            statistic = self.__dropper__.dropObject(STATISTIC_CLASS_NAME_ID)
            print('STATISTIC: ' + str(statistic))

    def dragEnterEvent(self, event):
        self.__dropper__.dragEnterEvent(event)
