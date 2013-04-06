'''
Created on 06-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar # @IgnorePep8
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycommon.actions import ActionSpec
    from pygui.qt.actions.actions_utils import create_action
    from pygui.qt.custom_widgets.filters import FiltersWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotNavigationToolbar(NavigationToolbar):

    def __init__(self, canvas, parent, **params):
        self.params = Params(**params)
        # create the default toolbar
        NavigationToolbar.__init__(self, canvas, parent)
        self.canvas = canvas

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
                                    handler=self.__showTachogramPlotSettings__,
                                    iconId='tachogram_plot_settings')
        self.addAction(tachogram_plot_settings_action)

        self.__normalPlot__()

        #add a filters combo box widget
        self.addWidget(FiltersWidget(parent,
                                     self.canvas.params.signal,
                                     self.canvas.params.annotation,
                                     clicked_handler=self.__filter_handler__))

        tachogram_plot_statistics_action = self.__createAction__(
                                title="Tachogram plot statistics",
                                handler=self.__showTachogramPlotStatistics__,
                                iconId='tachogram_plot_statistics')
        self.addAction(tachogram_plot_statistics_action)

    def __createAction__(self, **params):
        return create_action(self.parent(), ActionSpec(**params))

    def __normalPlot__(self):
        def __inner__(canvas):
            canvas.axes.plot(canvas.x, canvas.y)
        self.canvas.plot(__inner__)

    def __scatterPlot__(self):
        def __inner__(canvas):
            canvas.axes.plot(canvas.x, canvas.y, 'bo')
        self.canvas.plot(__inner__)

    def __filter_handler__(self, _signal, _annotation):
        self._views.clear()  # clear all remembered view history
        self.canvas.plot(force_plot=True, _signal=_signal)

    def __showTachogramPlotSettings__(self):
        if not self.params.show_tachogram_plot_settings_handler == None:
            self.params.show_tachogram_plot_settings_handler(
                                                    self.canvas.x_axis_unit)

    def __showTachogramPlotStatistics__(self):
        if not self.params.show_tachogram_plot_statistics_handler == None:
            self.params.show_tachogram_plot_statistics_handler()
