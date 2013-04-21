'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.widgets.dock_widget_widget import DockWidgetWidget
    from pygui.qt.widgets.splitter_widget import SplitterWidget
    from pygui.qt.custom_widgets.filters.filters_widget import FiltersWidget
    from pygui.qt.custom_widgets.filters.slave_annotation_filter_widget import SlaveAnnotationFilterWidget # @IgnorePep8
    from pygui.qt.custom_widgets.output_specification_widget import OutputSpecificationWidget  # @IgnorePep8
    from pygui.qt.plots.specific_widgets.miscellaneous_widget import MiscellaneousWidget # @IgnorePep8
    from pygui.qt.plots.specific_widgets.statistics_selection_widget import StatisticsSelectionWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PoincarePlotSettingsDockWidget(DockWidgetWidget):
    """
    a dock widget for poincare plot settings
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        super(PoincarePlotSettingsDockWidget, self).__init__(parent,
            title=params.get('title', 'Poincare plot settings'),
            dock_widget_location_changed=self.__dock_widget_location_changed__,
            **params)
        self.__splitter__ = SplitterWidget(self.dockComposite,
                                           orientation=Qt.Vertical)
        self.__splitter__.setHandleWidth(5)
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
        self.__createOutputSpecificationWidget__(QVBoxLayout())
        self.__createMiscellaneousWidget__(QVBoxLayout())
        self.__createStatisticsSelectionWidget__(QVBoxLayout())

    def __createFiltersWidget__(self, layout):
        self.__filtersWidget__ = FiltersWidget(
                        self.__splitter__,
                        layout=layout, data_accessor=self.data_accessor,
                        title='Active filters for tachogram plot',
                        use_apply_button=False,
                        annotation_widget_class=SlaveAnnotationFilterWidget)
        self.__changeSplitterHandleColor__(0, Qt.red)

    def __createOutputSpecificationWidget__(self, layout):
        self.__output_specification__ = OutputSpecificationWidget(
                                            self.__splitter__,
                                            no_custom_separator=True,
                                            layout=layout)
        self.__changeSplitterHandleColor__(1, Qt.blue)

    def __createMiscellaneousWidget__(self, layout):
        self.__output_specification__ = MiscellaneousWidget(
                                        self.__splitter__, layout=layout,
                                        data_accessor=self.data_accessor)
        self.__changeSplitterHandleColor__(2, Qt.green)

    def __createStatisticsSelectionWidget__(self, layout):
        self.__output_specification__ = StatisticsSelectionWidget(
                                            self.__splitter__, layout=layout)
        self.__changeSplitterHandleColor__(3, Qt.black)

    def __changeSplitterHandleColor__(self, idx, color):
        handle = self.__splitter__.handle(idx)
        p = handle.palette()
        p.setColor(handle.backgroundRole(), color)
        handle.setPalette(p)
        handle.setAutoFillBackground(True)
