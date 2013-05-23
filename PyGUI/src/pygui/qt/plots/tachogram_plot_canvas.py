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
    from pycore.collections_utils import pop_from_list
    from pymath.model.data_vector_listener import DataVectorListener
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
        self.canvas_title = TachogramPlotCanvasTitle()
        self.data_accessor = self.params.data_accessor  # alias
        self.data_accessor.addListener(self, __CanvasDataVectorListener__(self)) # @IgnorePep8
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)

        self.__current_plot_engine__ = None

        FigureCanvas.__init__(self, self.fig)
        self.title_text = self.fig.suptitle(self.canvas_title.title,
                                            fontsize=12)

        self.plot(NormalTachogramPlotEngine)

        # automatic layout adjustment to use available space more efficiently
        self.fig.tight_layout()
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.__dropper__ = CopyDropper(self, STATISTIC_MIME_ID)

    def plot(self, _plot_engine_class=None, force_plot=False):

        if self.__current_plot_engine__ == None:
            self.__current_plot_engine__ = NormalTachogramPlotEngine()
        #plot engine not specified and doesn't have to plot
        elif force_plot == False and (_plot_engine_class == None or \
            _plot_engine_class.__name__ == \
                self.__current_plot_engine__.__class__.__name__):
                return

        #plot engine class changed
        if not _plot_engine_class == None and not _plot_engine_class.__name__ \
            == self.__current_plot_engine__.__class__.__name__:
            self.__current_plot_engine__ = _plot_engine_class()
        self.axes.cla()
        self.__calculate__()
        self.__current_plot_engine__.plot(self)
        print('PLOTTING')

        self.axes.set_xlabel(self.data_accessor.signal_x_unit.display_label)
        self.axes.set_ylabel(self.data_accessor.signal_unit.display_label)
        self.title_text.set_text(self.canvas_title.title)
        self.draw()

    def dropEvent(self, event):
        if self.__dropper__.dropEvent(event):
            statistic = self.__dropper__.dropObject(STATISTIC_CLASS_NAME_ID)
            print('STATISTIC: ' + str(statistic))

    def dragEnterEvent(self, event):
        self.__dropper__.dragEnterEvent(event)

    def __calculate__(self):
        self.y = self.data_accessor.signal

        if self.data_accessor.signal_x_unit == OrderUnit:
            self.x = np.arange(0, len(self.y), 1)
        # x axis unit is the same as signal unit
        elif self.data_accessor.signal_x_unit == \
                                    self.data_accessor.signal_unit:
            self.x = np.cumsum(self.y)
        else:
            #express signal unit in terms of x axis unit
            multiplier = self.data_accessor.signal_unit.expressInUnit(
                                        self.data_accessor.signal_x_unit)
            self.x = np.cumsum(self.y) * multiplier

    @property
    def canvas_title(self):
        return self.__canvas_title__

    @canvas_title.setter
    def canvas_title(self, _canvas_title):
        self.__canvas_title__ = _canvas_title


class __CanvasDataVectorListener__(DataVectorListener):
    """
    class to run plot when signal, x axis unit is about to change
    """
    def __init__(self, _canvas):
        self.__canvas__ = _canvas

    def changeSignal(self, _signal, **params):
        self.__set_title__(**params)
        self.__canvas__.plot(force_plot=True)

    def changeAnnotation(self, _annotation, **params):
        self.__set_title__(**params)

    def changeXSignalUnit(self, _x_signal_unit, **params):
        self.__canvas__.plot(force_plot=True)

    def __set_title__(self, **params):
        params = Params(**params)
        if params.filter_name:
            self.__canvas__.canvas_title.addTitlePart('filtered',
                                                    params.filter_name)
        if params.remove_filter_names:
            self.__canvas__.canvas_title.removeTitlePart('filtered')


class NormalTachogramPlotEngine(object):
    """
    action invoked for 'normal' plot
    """
    def plot(self, _canvas):
        _canvas.axes.plot(_canvas.x, _canvas.y)


class ScatterTachogramPlotEngine(object):
    """
    action invoked for scatter plot
    """
    def plot(self, _canvas):
        _canvas.axes.plot(_canvas.x, _canvas.y, 'bo')


class HistogramTachogramPlotEngine(object):
    """
    action invoked for histogram plot
    """
    def plot(self, _canvas):
        _canvas.axes.grid(True)
        _canvas.axes.hist(_canvas.y, bins=20)
        #plt.hist(x, bins=10)
        #_canvas.axes.plot(_canvas.x, _canvas.y, 'bo')


class TachogramPlotCanvasTitle(object):
    """
    class used to create tachogram plot title
    """
    def __init__(self):
        self.__main_title__ = 'Tachogram plot'
        self.__title_parts__ = {}

    def addTitlePart(self, group, text):
        self.removeTitlePart(group, text)
        texts = self.__title_parts__.get(group, [])
        texts.append(text)
        self.__title_parts__[group] = texts

    def removeTitlePart(self, group, text=None):
        if text:
            pop_from_list(self.__title_parts__.get(group), text)
        else:
            self.__title_parts__.pop(group, None)

    @property
    def title(self):
        _title = self.__main_title__
        if len(self.__title_parts__):
            _title += ': '
        for group in self.__title_parts__:
            _title += "".join(['[', group, ':'])
            for idx, part in enumerate(self.__title_parts__[group]):
                _title += "".join([', ' if idx > 0 else '', part])
            _title += ']'
        return _title
