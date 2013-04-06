'''
Created on 15-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.units import get_unit_by_class_name
    from pymath.datasources import FileDataSource
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.plots.tachogram_plot_canvas import TachogramPlotCanvas
    from pygui.qt.plots.tachogram_plot_navigator_toolbar import TachogramPlotNavigationToolbar  # @IgnorePep8
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
        self.navigation_toolbar = TachogramPlotNavigationToolbar(self.canvas,
                            self,
                            show_tachogram_plot_settings_handler=self.params.show_tachogram_plot_settings_handler, # @IgnorePep8
                            show_tachogram_plot_statistics_handler=self.params.show_tachogram_plot_statistics_handler) # @IgnorePep8
        layout.addWidget(self.navigation_toolbar)

    def changeXUnit(self, _unit):
        self.canvas.changeXUnit(_unit)
