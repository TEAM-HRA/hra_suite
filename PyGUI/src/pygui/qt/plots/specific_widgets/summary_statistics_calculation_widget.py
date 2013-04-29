'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.misc import Params
    from pymath.model.data_vector_listener import DataVectorListener
    from pymath.model.core_parameters import CoreParameters
    from pymath.statistics.statistic_parameters import StatisticParameters
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
    from pygui.qt.plots.specific_widgets.summary_statistics_selection_widget import SummaryStatisticsSelectionWidget # @IgnorePep8
    from pygui.qt.plots.specific_widgets.statistics_calculation_progress_dialog_manager import PoincarePlotGeneratorProgressBar # @IgnorePep8    
except ImportError as error:
    ImportErrorMessage(error, __name__)


class SummaryStatisticsCalculationWidget(GroupBoxWidget):
    """
    widget adds an action of statistics calculations into summary
    statistics widget
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Summary statistics')
        super(SummaryStatisticsCalculationWidget, self).__init__(parent,
                                                                 **params)
        self.params = Params(**params)
        if self.params.data_accessor:
            self.params.data_accessor.addListener(self,
                          __SummaryStatisticsCalculationVectorListener__(self))

        self.__createButtons__()
        self.__statistics_selection__ = SummaryStatisticsSelectionWidget(self,
                    layout=QVBoxLayout(), i18n_def='Selection',
                    change_selection_count_handler=self.__change_selection_count_handler__) # @IgnorePep8

    def __createButtons__(self):
        buttons_composite = CompositeWidget(self, layout=QHBoxLayout())
        self.__calculate_button__ = PushButtonWidget(
                    buttons_composite,
                    i18n_def="Calculate summary statistics",
                    clicked_handler=self.__calculate_statistics_handler__,
                    enabled=False)

    def __calculate_statistics_handler__(self):
        if self.params.data_accessor:
            self.params.data_accessor.prepareParametersContainer()

            formatted_summary_statistics = []
            pp_generator_progress_bar = PoincarePlotGeneratorProgressBar(self,
                                [self.params.data_accessor],
                                label_text='Summary statistics calculation',
                                check_level=CoreParameters.LOW_CHECK_LEVEL,
                    formatted_summary_statistics=formatted_summary_statistics)
            pp_generator_progress_bar.start()
            if pp_generator_progress_bar.interrupted() == False:
                self.__statistics_selection__.setStatisticsValues(
                                            formatted_summary_statistics[0])

    def __change_selection_count_handler__(self, _count):
        """
        handler invoked when number of selected rows is changing
        """
        self.__calculate_button__.setEnabled(_count > 0)


class __SummaryStatisticsCalculationVectorListener__(DataVectorListener):
    """
    data accessor listener used to set up some statistics parameters
    concerning summary statistics
    """
    def __init__(self, _summary_statistics_calculation_widget):
        self.__summary_statistics_calculation_widget__ = _summary_statistics_calculation_widget  # @IgnorePep8

    def prepareParameters(self, data_vector_accessor):
        w = self.__summary_statistics_calculation_widget__  # alias

        container = data_vector_accessor.parameters_container
        parameters = container.getParametersObject(
                                StatisticParameters.NAME, StatisticParameters)
        parameters.clearSummaryStatisticsClasses()
        parameters.summary_statistics_classes = w.__statistics_selection__.getSelectedStatisticsClasses() # @IgnorePep8
