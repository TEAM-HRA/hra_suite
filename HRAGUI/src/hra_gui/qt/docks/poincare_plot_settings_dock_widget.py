'''
Created on 04-04-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_gui.qt.widgets.dock_widget_widget import DockWidgetWidget
    from hra_gui.qt.widgets.splitter_widget import SplitterWidget
    from hra_gui.qt.custom_widgets.filters.filters_widget import FiltersWidget
    from hra_gui.qt.custom_widgets.filters.slave_annotation_filter_widget import SlaveAnnotationFilterWidget # @IgnorePep8
    from hra_gui.qt.custom_widgets.output_specification_widget import OutputSpecificationWidget  # @IgnorePep8
    from hra_gui.qt.plots.specific_widgets.miscellaneous_widget import MiscellaneousWidget # @IgnorePep8
    from hra_gui.qt.plots.specific_widgets.statistics_widget import StatisticsWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PoincarePlotSettingsDockWidget(DockWidgetWidget):
    """
    a dock widget for poincare plot settings
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)

        self.__splitter_idx__ = 0
        self.data_vectors_accessor_group = \
            self.params.data_vectors_accessor_group  # alias
        if not self.data_vectors_accessor_group == None:
            self.main_data_accessor = \
                self.data_vectors_accessor_group.group_data_vector_accessor
        else:
            self.main_data_accessor = self.params.data_accessor  # alias

        super(PoincarePlotSettingsDockWidget, self).__init__(parent,
                title=params.get('title', 'Poincare plot settings'), **params)
        self.__splitter__ = SplitterWidget(self.dockComposite,
                                           orientation=Qt.Vertical)
        self.__splitter__.setHandleWidth(5)

        self.__createStatisticsWidget__(QVBoxLayout())
        self.__createFiltersWidget__(QHBoxLayout())
        self.__createOutputSpecificationWidget__(QVBoxLayout())
        self.__createMiscellaneousWidget__(QVBoxLayout())

        parent.addDockWidget(Qt.LeftDockWidgetArea, self)

    def __changeUnit__(self, unit):
        if not self.main_data_accessor == None:
            self.main_data_accessor.changeXSignalUnit(self, unit)

    def __createFiltersWidget__(self, layout):
        FiltersWidget(self.__splitter__,
                        layout=layout, data_accessor=self.main_data_accessor,
                        title='Active filters for tachogram plot',
                        use_apply_button=False,
                        annotation_widget_class=SlaveAnnotationFilterWidget)
        self.__splitter__.changeSplitterHandleColor(self.__splitter_idx__,
                                                    Qt.red)
        self.__splitter_idx__ += 1

    def __createOutputSpecificationWidget__(self, layout):
        OutputSpecificationWidget(self.__splitter__, no_custom_separator=True,
                        layout=layout, data_accessor=self.main_data_accessor)
        self.__splitter__.changeSplitterHandleColor(self.__splitter_idx__,
                                                    Qt.blue)
        self.__splitter_idx__ += 1

    def __createMiscellaneousWidget__(self, layout):
        MiscellaneousWidget(self.__splitter__, layout=layout,
                            data_accessor=self.main_data_accessor)
        self.__splitter__.changeSplitterHandleColor(self.__splitter_idx__,
                                                    Qt.green)
        self.__splitter_idx__ += 1

    def __createStatisticsWidget__(self, layout):
        self.__statistics_widget__ = StatisticsWidget(self.__splitter__,
            layout=layout, data_accessor=self.main_data_accessor,
            data_vectors_accessor_group=self.data_vectors_accessor_group,
            output_file_listener=self.params.output_file_listener,
            save_outcomes_fixed_state=self.params.save_outcomes_fixed_state)
        self.__splitter__.changeSplitterHandleColor(self.__splitter_idx__,
                                                    Qt.black)
        self.__splitter_idx__ += 1
