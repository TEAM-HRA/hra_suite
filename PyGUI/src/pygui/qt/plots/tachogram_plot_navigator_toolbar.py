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
    from pygui.qt.plots.tachogram_plot_canvas import NormalTachogramPlotEngine
    from pygui.qt.plots.tachogram_plot_canvas import ScatterTachogramPlotEngine
    from pygui.qt.plots.tachogram_plot_canvas import HistogramTachogramPlotEngine # @IgnorePep8
    from pygui.qt.plots.tachogram_plot_settings_dock_widget import TachogramPlotSettingsDockWidget # @IgnorePep8
    from pygui.qt.plots.tachogram_plot_statistics_dock_widget import TachogramPlotStatisticsDockWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotNavigationToolbar(NavigationToolbar):

    def __init__(self, parent, canvas, **params):
        self.params = Params(**params)
        # create the default toolbar
        NavigationToolbar.__init__(self, canvas, parent)
        self.canvas = canvas
        self.data_accessor = self.params.data_accessor  # alias

        # add new toolbar buttons
        normal_plot_action = self.__createAction__(title="Normal plot",
                                            handler=self.__normalPlot__,
                                            iconId='graph_button')
        self.addAction(normal_plot_action)

        scatter_plot_action = self.__createAction__(title="Scatter plot",
                                            handler=self.__scatterPlot__,
                                            iconId='scatter_plot_button')
        self.addAction(scatter_plot_action)

        histogram_plot_action = self.__createAction__(title="Histogram plot",
                                            handler=self.__histogramPlot__,
                                            iconId='histogram_plot_button')
        self.addAction(histogram_plot_action)

        tachogram_plot_settings_action = self.__createAction__(
                                    title="Tachogram plot settings",
                                    handler=self.__showTachogramPlotSettings__,
                                    iconId='tachogram_plot_settings')
        self.addAction(tachogram_plot_settings_action)

        tachogram_plot_statistics_action = self.__createAction__(
                                title="Tachogram plot statistics",
                                handler=self.__showTachogramPlotStatistics__,
                                iconId='tachogram_plot_statistics')
        self.addAction(tachogram_plot_statistics_action)

    def __createAction__(self, **params):
        return create_action(self.parent(), ActionSpec(**params))

    def __normalPlot__(self):
        self.canvas.plot(NormalTachogramPlotEngine)

    def __scatterPlot__(self):
        self.canvas.plot(ScatterTachogramPlotEngine)

    def __histogramPlot__(self):
        self.canvas.plot(HistogramTachogramPlotEngine)

    def __showTachogramPlotSettings__(self):
        if not hasattr(self, '__tachogram_settings__'):
            parent = self.params.dock_parent \
                    if self.params.dock_parent else self.parent()
            self.__tachogram_settings__ = TachogramPlotSettingsDockWidget(
                                parent, data_accessor=self.data_accessor)
        self.__tachogram_settings__.show()

    def __showTachogramPlotStatistics__(self):
        if not hasattr(self, '__tachogram_statistics__'):
            parent = self.params.dock_parent \
                    if self.params.dock_parent else self.parent()
            self.__tachogram_statistics__ = TachogramPlotStatisticsDockWidget(
                                parent, data_accessor=self.data_accessor)
        self.__tachogram_statistics__.show()
