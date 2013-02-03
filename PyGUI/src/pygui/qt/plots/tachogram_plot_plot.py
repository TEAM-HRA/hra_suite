'''
Created on 15-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
from pygui.qt.utils.widgets import PushButtonCommon
from pycommon.actions import ActionSpec
from pygui.qt.actions.actions_utils import create_action
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pymath.datasources import FileDataSource
    from pygui.qt.utils.widgets import CompositeCommon
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas # @IgnorePep8
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar # @IgnorePep8
    import numpy as np
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
        file_data_source = FileDataSource(**file_data_source_params)
        data_source = file_data_source.getDataSource()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.canvas = TachogramPlotCanvas(self,
                                    signal=data_source.signal,
                                    annotation=data_source.annotation)
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
        self.x = np.arange(0.0, len(self.params.signal), 1)
        self.y = self.params.signal
        self.axes.scatter(self.x, self.y)
        #self.axes.plot(self.x, self.y)
        #self.axes.plot(self.y)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class TachogramNavigationToolbar(NavigationToolbar):

    def __init__(self, canvas, parent):
        # create the default toolbar
        NavigationToolbar.__init__(self, canvas, parent)
        self.canvas = canvas
        # add new toolbar buttons

        normal_plot_action = self.__createAction__(title="Normal plot",
                                            handler=self.__normalPlot__,
                                            iconId='graph_button')
        self.addAction(normal_plot_action)

        scatter_plot_action = self.__createAction__(title="Scatter plot",
                                            handler=self.__scatterlPlot__,
                                            iconId='scatter_plot_button')
        self.addAction(scatter_plot_action)

    def __normalPlot__(self):
        self.canvas.axes.cla()
        self.canvas.axes.plot(self.canvas.x, self.canvas.y)
        self.canvas.draw()

    def __scatterlPlot__(self):
        self.canvas.axes.cla()
        self.canvas.axes.scatter(self.canvas.x, self.canvas.y)
        self.canvas.draw()

    def __createAction__(self, **params):
        return create_action(self.parent(), ActionSpec(**params))

#    def __init2__(self, **params):
#        self.params = Params(**params)
#        self.__iconId = self.params.iconId
#        self.__tipId = self.params.tipId
#        self.__signal = self.params.signal
#        self.__slot = self.params.handler
#        self.__title = self.params.title
#        self.__checkable = ("True" == str(self.params.checkable))
