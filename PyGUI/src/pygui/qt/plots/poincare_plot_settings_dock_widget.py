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
    from pygui.qt.utils.widgets import DockWidgetCommon
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.custom_widgets.filters.filters_widget import FiltersWidget
    from pygui.qt.custom_widgets.filters.slave_annotation_filter_widget import SlaveAnnotationFilterWidget #  @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PoincarePlotSettingsDockWidget(DockWidgetCommon):
    """
    a dock widget for poincare plot settings
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        get_or_put(params, 'dock_widget_location_changed',
                   self.__dock_widget_location_changed__)
        super(PoincarePlotSettingsDockWidget, self).__init__(parent,
                        title=params.get('title', 'Poincare plot settings'),
                        **params)
        self.setObjectName("PoincarePlotSettingsDockWidget")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea |
                             Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        layout = QVBoxLayout()
        layout.setMargin(0)  # no margin for internal layout
        self.dockComposite = CompositeCommon(self, layout=layout,
                                        not_add_widget_to_parent_layout=True)

        self.setWidget(self.dockComposite)
        parent.addDockWidget(Qt.LeftDockWidgetArea, self)

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

        #in order to recreate filters widget at first we have to remove
        #previous version
        if hasattr(self, '__filtersWidget__'):
            self.__filtersWidget__.hide()
            layout.removeWidget(self.__filtersWidget__)

        if dockWidgetArea in [Qt.TopDockWidgetArea, Qt.BottomDockWidgetArea]:
            self.__createFiltersWidget__(QVBoxLayout())
        else:
            self.__createFiltersWidget__(QHBoxLayout())

    def __createFiltersWidget__(self, layout):
        self.__filtersWidget__ = FiltersWidget(self.dockComposite,
                        layout=layout, data_accessor=self.data_accessor,
                        title='Active filters for tachogram plot',
                        use_button_active=True,
                        annotation_widget_class=SlaveAnnotationFilterWidget)
