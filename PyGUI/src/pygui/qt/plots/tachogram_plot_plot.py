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
    from pycommon.actions import ActionSpec
    from pymath.datasources import FileDataSource
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.actions.actions_utils import create_action
    from pygui.qt.custom_widgets.filters import FiltersWidget
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
                                          annotation=data.annotation)
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
        #self.x = np.arange(0.0, 3.0, 0.01)
        #self.y = np.cos(2 * np.pi * self.x)
        #self.x = np.arange(0.0, len(self.params.signal), 1)
        self.calculate(self.params.signal)
        #self.x = np.arange(0, len(self.params.signal), 1)
        #self.y = self.params.signal
        FigureCanvas.__init__(self, self.fig)

        # automatic layout adjustment to use available space more efficiently
        self.fig.tight_layout()
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def calculate(self, _signal):
        self.x = np.arange(0, len(_signal), 1)
        self.y = _signal


class TachogramNavigationToolbar(NavigationToolbar):

    def __init__(self, canvas, parent):
        # create the default toolbar
        NavigationToolbar.__init__(self, canvas, parent)
        self.canvas = canvas
        self.__current_plot__ = None
        self.__signal_unit__ = parent.signal_unit
        # add new toolbar buttons

        normal_plot_action = self.__createAction__(title="Normal plot",
                                            handler=self.__normalPlot__,
                                            iconId='graph_button')
        self.addAction(normal_plot_action)

        scatter_plot_action = self.__createAction__(title="Scatter plot",
                                            handler=self.__scatterPlot__,
                                            iconId='scatter_plot_button')
        self.addAction(scatter_plot_action)
        self.__normalPlot__()

        #add a filters combo box widget
        self.addWidget(FiltersWidget(parent,
                                     self.canvas.params.signal,
                                     self.canvas.params.annotation,
                                     clicked_handler=self.__filter_handler__))

    def __normalPlot__(self, force_plot=False):
        if self.__check_plot__(self.__normalPlot__, force_plot) == True:
            self.canvas.axes.cla()
            self.canvas.axes.plot(self.canvas.x, self.canvas.y)
#        print('self.canvas.axes.get_xlim(): ' + str(self.canvas.axes.get_xlim())) # @IgnorePep8
#        print('self.canvas.x.min(): ' + str(self.canvas.x.min())
#               + ' self.canvas.x.max(): ' + str(self.canvas.x.max())) # @IgnorePep8
            self.canvas.axes.set_ylabel(self.__signal_unit__.display_label)
            self.canvas.draw()

    def __scatterPlot__(self, force_plot=False):
        if self.__check_plot__(self.__scatterPlot__, force_plot) == True:
            self.canvas.axes.cla()
            #self.canvas.axes.xrange(0, self.canvas.x.max())
            #self.canvas.axes.set_xlim((self.canvas.x.min(), self.canvas.x.max() + 10000)) # @IgnorePep8
            #self.canvas.axes.set_ylim((self.canvas.y.min(), self.canvas.y.max() + 1000)) # @IgnorePep8
            #ax.set_ylim((-2,2))
            self.canvas.axes.plot(self.canvas.x, self.canvas.y, 'bo')
            #self.canvas.axes.scatter(self.canvas.x, self.canvas.y)
            self.canvas.axes.set_ylabel(self.__signal_unit__.display_label)
            self.canvas.draw()

    def __createAction__(self, **params):
        return create_action(self.parent(), ActionSpec(**params))

    def __filter_handler__(self, _signal, _annotation):
        self._views.clear()  # clear all remembered view history
        self.canvas.calculate(_signal)
        self.__current_plot__(force_plot=True)

    def __check_plot__(self, _plot, force_plot=False):
        if force_plot == False and self.__current_plot__ == _plot:
            return False
        self.__current_plot__ = _plot
        return True
