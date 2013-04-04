'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.collections_utils import nvl
    from pycore.misc import Params
    from pycore.units import OrderUnit
    from pygui.qt.utils.widgets import DockWidgetCommon
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.custom_widgets.units import TimeUnitsWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotSettingsDockWidget(DockWidgetCommon):
    """
    a dock widget for tachogram plot settings
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
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

        self.__x_unit__ = OrderUnit
        self.__createUnitsWidget__(QHBoxLayout())

        self.setWidget(self.dockComposite)
        parent.addDockWidget(Qt.BottomDockWidgetArea, self)
        self.change_unit_handler = params.get('change_unit_handler')

    def __changeUnit__(self, unit):
        if not self.change_unit_handler == None:
            self.__x_unit__ = unit
            self.change_unit_handler(unit)

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
                    default_unit=nvl(self.__x_unit__, self.params.x_unit,
                                     OrderUnit),
                    change_unit_handler=self.__changeUnit__,
                    layout=layout)
        self.unitsWidget.addUnit(OrderUnit)
