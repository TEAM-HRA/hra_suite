'''
Created on 04-04-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_core.units import get_unit_by_class_name
    from hra_math.model.data_vector_accessor import get_data_accessor_from_file_specification # @IgnorePep8
    from hra_gui.qt.utils.signals import SignalDispatcher
    from hra_gui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.main_window_widget import MainWindowWidget
    from hra_gui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from hra_gui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from hra_gui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
    from hra_gui.qt.plots.tachogram_plot_canvas import TachogramPlotCanvas
    from hra_gui.qt.plots.tachogram_plot_navigator_toolbar import TachogramPlotNavigationToolbar  # @IgnorePep8
    from hra_gui.qt.plots.specific_widgets.poincare_toolbar_widget import PoincareToolBarWidget  # @IgnorePep8
    from hra_gui.qt.docks.poincare_plot_settings_dock_widget import PoincarePlotSettingsDockWidget  # @IgnorePep8
    from hra_gui.qt.docks.outcome_files_tracker_dock_widget import OutcomeFilesTrackerDockWidget # @IgnorePep8
    from hra_gui.qt.docks.poincare_plot_movie_dock_widget import PoincarePlotMovieDockWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotCompositeWidget(MainWindowWidget):
    def __init__(self, parent, **params):
        super(TachogramPlotCompositeWidget, self).__init__(parent, **params)
        self.params = Params(**params)
        self.data_accessor = get_data_accessor_from_file_specification(self,
                                                self.params.file_specification)

        self.addToolBar(OperationalToolBarWidget(self))
        self.addToolBar(PoincareToolBarWidget(self))

        signal_unit = get_unit_by_class_name(
                        self.params.file_specification.signal_unit_class_name)
        self.setCentralWidget(__TachogramPlot__(self, signal_unit=signal_unit))

    def toolbar_maximum_handler(self):
        SignalDispatcher.broadcastSignal(MAXIMIZE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_restore_handler(self):
        SignalDispatcher.broadcastSignal(RESTORE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_close_handler(self):
        SignalDispatcher.broadcastSignal(CLOSE_TACHOGRAM_PLOT_SIGNAL, self)

    def show_poincare_settings_handler(self):
        if not hasattr(self, '__poincare_settings__'):
            self.__poincare_settings__ = PoincarePlotSettingsDockWidget(
                        self, data_accessor=self.data_accessor,
                        output_file_listener=self.__output_file_listener__)
        self.__poincare_settings__.show()
#    def __change_unit_handler__(self, _unit):
#        self.tachogramPlot.changeXUnit(_unit)
#        statusbar = StatusBarWidget(self.__initial_tab__)
#        self.__initial_tab__.setStatusBar(statusbar)
#        statusLabel = LabelWidget(statusbar,
#                    i18n_def="STATUS",
#                    add_widget_to_parent=True)
#

    def __output_file_listener__(self, _filename):
        if not hasattr(self, '__outcome_files_tracker__'):
            self.__outcome_files_tracker__ = OutcomeFilesTrackerDockWidget(
                                                                        self)
        self.__outcome_files_tracker__.show()
        self.__outcome_files_tracker__.appendFile(_filename)

    @property
    def file_specification(self):
        """
        property method returns file_specification object associate with
        tachogram plot window
        """
        return self.params.file_specification

    def show_poincare_movie_handler(self):
        if not hasattr(self, '__poincare_movie__'):
            self.__poincare_movie__ = PoincarePlotMovieDockWidget(
                        self, data_accessor=self.data_accessor,
                        output_file_listener=self.__output_file_listener__)
        self.__poincare_movie__.show()


class __TachogramPlot__(CompositeWidget):
    """
    this class represents core of the tachogram plot that is a plot itself
    """
    def __init__(self, parent, **params):
        super(__TachogramPlot__, self).__init__(parent,
                                        not_add_widget_to_parent_layout=True)
        self.params = Params(**params)
        self.signal_unit = self.params.signal_unit

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.canvas = TachogramPlotCanvas(self,
                                          data_accessor=parent.data_accessor)
        layout.addWidget(self.canvas)
        self.navigation_toolbar = TachogramPlotNavigationToolbar(
                                    self, self.canvas, dock_parent=parent,
                                    data_accessor=parent.data_accessor)
        layout.addWidget(self.navigation_toolbar)
