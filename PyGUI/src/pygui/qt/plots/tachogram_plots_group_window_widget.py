'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.main_window_widget import MainWindowWidget
    from pygui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotsGroupWindowWidget(MainWindowWidget):
    """
    initial tachogram plot window used to take operations
    on the whole group of tachogram plots
    """
    def __init__(self, parent, **params):
        super(TachogramPlotsGroupWindowWidget, self).__init__(parent, **params)
        self.params = Params(**params)

        self.addToolBar(OperationalToolBarWidget(self))

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        composite = CompositeWidget(self,
                            sizePolicy=sizePolicy,
                            not_add_widget_to_parent_layout=True)
        self.setCentralWidget(composite)
        self.__file_specifications__ = []

#        self.tachogramPlot = __TachogramPlot__(self,
#                        file_specification=_files_specifications[0])
#        self.setCentralWidget(self.tachogramPlot)

    def toolbar_maximum_handler(self):
        SignalDispatcher.broadcastSignal(MAXIMIZE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_restore_handler(self):
        SignalDispatcher.broadcastSignal(RESTORE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_close_handler(self):
        SignalDispatcher.broadcastSignal(CLOSE_TACHOGRAM_PLOT_SIGNAL, self)

    def addFileSpecification(self, _file_specification):
        if self.__file_specifications__.count(_file_specification) == 0:
            self.__file_specifications__.append(_file_specification)
#    def __change_unit_handler__(self, _unit):
#        self.tachogramPlot.changeXUnit(_unit)
#        statusbar = StatusBarWidget(self.__initial_tab__)
#        self.__initial_tab__.setStatusBar(statusbar)
#        statusLabel = LabelWidget(statusbar,
#                    i18n_def="STATUS",
#                    add_widget_to_parent=True)
#


#class __TachogramPlot__(CompositeWidget):
#    """
#    this class represents core of the tachogram plot that is a plot itself
#    """
#    def __init__(self, parent, **params):
#        super(__TachogramPlot__, self).__init__(parent,
#                                        not_add_widget_to_parent_layout=True)
#        self.params = Params(**params)
#        file_data_source_params = self.params.file_specification._asdict()
#        self.signal_unit = get_unit_by_class_name(
#                        file_data_source_params.get('signal_unit_class_name'))
#        file_data_source = FileDataSource(**file_data_source_params)
#        layout = QVBoxLayout()
#        self.setLayout(layout)
#        data = file_data_source.getData()
#        data_accessor = DataVectorAccessor(data)
#        data_accessor.source_name = file_data_source.source_filename
#        data_accessor.changeXSignalUnit(self, OrderUnit)
#        self.canvas = TachogramPlotCanvas(self, data_accessor=data_accessor)
#        layout.addWidget(self.canvas)
#        self.navigation_toolbar = TachogramPlotNavigationToolbar(
#                                                self, self.canvas,
#                                                dock_parent=parent,
#                                                data_accessor=data_accessor)
#        layout.addWidget(self.navigation_toolbar)
