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
    from pygui.qt.plots.specific_widgets.summary_statistics_selection_widget import SummaryStatisticsSelectionWidget # @IgnorePep8
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
                title=params.get('title', 'Poincare plot settings'), **params)
        self.__splitter__ = SplitterWidget(self.dockComposite,
                                           orientation=Qt.Vertical)
        self.__splitter__.setHandleWidth(5)

        self.__createFiltersWidget__(QHBoxLayout())
        self.__createOutputSpecificationWidget__(QVBoxLayout())
        self.__createMiscellaneousWidget__(QVBoxLayout())
        self.__createStatisticsSelectionWidget__(QVBoxLayout())
        self.__createSummaryStatisticsSelectionWidget__(QVBoxLayout())

        parent.addDockWidget(Qt.LeftDockWidgetArea, self)

    def __changeUnit__(self, unit):
        if not self.data_accessor == None:
            self.data_accessor.changeXSignalUnit(self, unit)

    def __createFiltersWidget__(self, layout):
        FiltersWidget(self.__splitter__,
                        layout=layout, data_accessor=self.data_accessor,
                        title='Active filters for tachogram plot',
                        use_apply_button=False,
                        annotation_widget_class=SlaveAnnotationFilterWidget)
        self.__splitter__.changeSplitterHandleColor(0, Qt.red)

    def __createOutputSpecificationWidget__(self, layout):
        OutputSpecificationWidget(self.__splitter__, no_custom_separator=True,
                                  layout=layout)
        self.__splitter__.changeSplitterHandleColor(1, Qt.blue)

    def __createMiscellaneousWidget__(self, layout):
        MiscellaneousWidget(self.__splitter__, layout=layout,
                            data_accessor=self.data_accessor)
        self.__splitter__.changeSplitterHandleColor(2, Qt.green)

    def __createStatisticsSelectionWidget__(self, layout):
        StatisticsSelectionWidget(self.__splitter__, layout=layout)
        self.__splitter__.changeSplitterHandleColor(3, Qt.black)

    def __createSummaryStatisticsSelectionWidget__(self, layout):
        SummaryStatisticsSelectionWidget(self.__splitter__, layout=layout)
        self.__splitter__.changeSplitterHandleColor(4, Qt.yellow)
