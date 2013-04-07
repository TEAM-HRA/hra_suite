'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.misc import Params
    from pycore.units import OrderUnit
    from pygui.qt.utils.widgets import DockWidgetCommon
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.custom_widgets.units import TimeUnitsWidget
    #from pygui.qt.custom_widgets.filters import FiltersWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotSettingsDockWidget(DockWidgetCommon):
    """
    a dock widget for tachogram plot settings
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        get_or_put(params, 'dock_widget_location_changed',
                   self.__dock_widget_location_changed__)
        super(TachogramPlotSettingsDockWidget, self).__init__(parent,
                        title=params.get('title', 'Tachogram plot settings'),
                        **params)
        self.setObjectName("TachogramPlotSettingsDockWidget")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea |
                             Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        layout = QVBoxLayout()
        layout.setMargin(0)  # no margin for internal layout
        self.dockComposite = CompositeCommon(self, layout=layout,
                                        not_add_widget_to_parent_layout=True)

        self.__createUnitsWidget__(QHBoxLayout())
        #self.__createFiltersWidget__()

        self.setWidget(self.dockComposite)
        parent.addDockWidget(Qt.BottomDockWidgetArea, self)

    def __changeUnit__(self, unit):
        if not self.data_accessor == None:
            self.data_accessor.changeXSignalUnit(self, unit)

    def __dock_widget_location_changed__(self, dockWidgetArea):
        layout = self.layout()
        if (dockWidgetArea in [Qt.TopDockWidgetArea, Qt.BottomDockWidgetArea]
            and isinstance(layout, QHBoxLayout)) or \
            (dockWidgetArea in [Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea]
            and isinstance(layout, QVBoxLayout)):
            return

        self.unitsWidget.hide()
        layout.removeWidget(self.unitsWidget)
        if dockWidgetArea in [Qt.TopDockWidgetArea, Qt.BottomDockWidgetArea]:
            self.__createUnitsWidget__(QHBoxLayout())
        else:
            self.__createUnitsWidget__(QVBoxLayout())

    def __createUnitsWidget__(self, layout):
        self.unitsWidget = TimeUnitsWidget(self.dockComposite,
                                i18n_def='X axis units',
                                default_unit=self.data_accessor.signal_x_unit,
                                change_unit_handler=self.__changeUnit__,
                                layout=layout)
        self.unitsWidget.addUnit(OrderUnit)

#    def __createFiltersWidget__(self):
#        FiltersWidget(self.dockComposite,
#                                     self.canvas.params.signal,
#                                     self.canvas.params.annotation,
#                                     clicked_handler=self.__filter_handler__)
