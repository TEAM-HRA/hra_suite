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
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
    from pygui.qt.plots.specific_widgets.statistics_selection_widget import StatisticsSelectionWidget # @IgnorePep8
    from pygui.qt.plots.specific_widgets.summary_statistics_selection_widget import SummaryStatisticsSelectionWidget  # @IgnorePep8
    from pygui.qt.plots.specific_widgets.poincare_plot_generator_progress_bar import PoincarePlotGeneratorProgressBar # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class StatisticsWidget(GroupBoxWidget):
    """
    widget adds an action of statistics calculations into statistics widget
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Statistics')
        super(StatisticsWidget, self).__init__(parent, **params)
        self.params = Params(**params)
        if self.params.data_accessor:
            self.params.data_accessor.addListener(self,
                                        __StatisticsVectorListener__(self))

        self.__createButtons__()
        self.__statistics_widget__ = StatisticsSelectionWidget(self,
                    layout=QVBoxLayout(), i18n_def='',
                    check_handler=self.__change_statistics_handler__)

        self.__summary_statistics_widget__ = SummaryStatisticsSelectionWidget(
                    self, layout=QVBoxLayout(), i18n_def='Summary statistics',
                    check_handler=self.__change_statistics_handler__)

    def __createButtons__(self):
        buttons_composite = CompositeWidget(self, layout=QHBoxLayout())
        self.__calculate_button__ = PushButtonWidget(buttons_composite,
                    i18n_def="Calculate statistics",
                    clicked_handler=self.__calculate_statistics_handler__,
                    enabled=False)
        self.__save_outcomes_button__ = CheckBoxWidget(buttons_composite,
                                    i18n_def="Save outcomes", enabled=False)

    def __calculate_statistics_handler__(self):
        if self.params.data_accessor:
            self.params.data_accessor.prepareParametersContainer()

            formatted_summary_statistics = []
            save_csv = self.__save_outcomes_button__.isChecked()
            check_level = CoreParameters.MEDIUM_CHECK_LEVEL if save_csv else CoreParameters.LOW_CHECK_LEVEL # @IgnorePep8
            pp_generator_progress_bar = PoincarePlotGeneratorProgressBar(self,
                    [self.params.data_accessor],
                    label_text='Statistics calculation',
                    check_level=check_level, save_csv=save_csv,
                    formatted_summary_statistics=formatted_summary_statistics,
                    output_file_listener=self.params.output_file_listener)
            pp_generator_progress_bar.start()
            if pp_generator_progress_bar.interrupted() == False and \
                len(formatted_summary_statistics) == 1:
                self.__summary_statistics_widget__.setStatisticsValues(
                                            formatted_summary_statistics[0])

    def __change_statistics_handler__(self, _statistic, _checked):
        """
        handler invoked when number of selected rows is changing
        """
        if not _checked:
            if len(self.getSelectedStatisticsClasses()) > 0 or \
                len(self.getSelectedSummaryStatisticsClasses()) > 0:
                _checked = True
        self.__calculate_button__.setEnabled(_checked)
        self.__save_outcomes_button__.setEnabled(_checked)

    def getSelectedStatisticsClasses(self):
        return self.__statistics_widget__.getSelectedStatisticsClasses()

    def getSelectedSummaryStatisticsClasses(self):
        return self.__summary_statistics_widget__.getSelectedStatisticsClasses() # @IgnorePep8


class __StatisticsVectorListener__(DataVectorListener):
    """
    data accessor listener used to set up some statistics parameters
    concerning statistics
    """
    def __init__(self, _statistics_widget):
        self.__statistics_widget__ = _statistics_widget

    def prepareParameters(self, data_vector_accessor):
        w = self.__statistics_widget__  # alias

        container = data_vector_accessor.parameters_container
        parameters = container.getParametersObject(
                                StatisticParameters.NAME, StatisticParameters)

        parameters.clearStatisticsClasses()
        parameters.statistics_classes = w.getSelectedStatisticsClasses()

        parameters.clearSummaryStatisticsClasses()
        parameters.summary_statistics_classes = \
                            w.getSelectedSummaryStatisticsClasses()