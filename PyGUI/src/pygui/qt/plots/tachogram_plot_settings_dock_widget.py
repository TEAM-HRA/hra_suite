'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.units import OrderUnit
    from pygui.qt.widgets.dock_widget_widget import DockWidgetWidget
    from pygui.qt.custom_widgets.units import TimeUnitsWidget
    from pygui.qt.custom_widgets.filters.filters_widget import FiltersWidget
    from pygui.qt.custom_widgets.filters.master_annotation_filter_widget import MasterAnnotationFilterWidget  # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotSettingsDockWidget(DockWidgetWidget):
    """
    a dock widget for tachogram plot settings
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        super(TachogramPlotSettingsDockWidget, self).__init__(parent,
            title=params.get('title', 'Tachogram plot settings'),
            **params)

        self.__createUnitsWidget__(QHBoxLayout())
        self.__createFiltersWidget__(QVBoxLayout())

        parent.addDockWidget(Qt.BottomDockWidgetArea, self)

    def __changeUnit__(self, unit):
        if not self.data_accessor == None:
            self.data_accessor.changeXSignalUnit(self, unit)

    def __createUnitsWidget__(self, layout):
        self.__unitsWidget__ = TimeUnitsWidget(self.dockComposite,
                                i18n_def='X axis units',
                                default_unit=self.data_accessor.signal_x_unit,
                                change_unit_handler=self.__changeUnit__,
                                layout=layout)
        self.__unitsWidget__.addUnit(OrderUnit)

    def __createFiltersWidget__(self, layout):
        self.__filtersWidget__ = FiltersWidget(self.dockComposite,
                        layout=layout, data_accessor=self.data_accessor,
                        annotation_widget_class=MasterAnnotationFilterWidget,
                        use_apply_button=True,
                        restore_button=True)
