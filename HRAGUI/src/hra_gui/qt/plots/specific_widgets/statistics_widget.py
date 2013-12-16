'''
Created on 04-04-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_core.collections_utils import get_or_put
    from hra_core.misc import Params
    from hra_math.model.data_vector_listener import DataVectorListener
    from hra_math.model.parameters.core_parameters import CoreParameters
    from hra_math.model.parameters.poincare_plot_parameters \
        import PoincarePlotParameters
    from hra_gui.qt.widgets.group_box_widget import GroupBoxWidget
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.check_box_widget import CheckBoxWidget
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.plots.specific_widgets.statistics_selection_widget \
        import StatisticsSelectionWidget
    from hra_gui.qt.plots.specific_widgets.summary_statistics_selection_widget import SummaryStatisticsSelectionWidget  # @IgnorePep8
    from hra_gui.qt.plots.specific_widgets.poincare_plot_generator_progress_bar import PoincarePlotGeneratorProgressBar # @IgnorePep8
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

        self.data_accessors = []
        self.main_data_accessor = None
        if not self.params.data_vectors_accessor_group == None:
            self.data_accessors = self.params.data_vectors_accessor_group.data_vectors_accessors # @IgnorePep8
            self.main_data_accessor = self.params.data_vectors_accessor_group.group_data_vector_accessor # @IgnorePep8
        elif not self.params.data_accessor == None:
            self.main_data_accessor = self.params.data_accessor
            self.data_accessors = [self.main_data_accessor]

        for data_accessor in self.data_accessors:
            data_accessor.addListener(self, __StatisticsVectorListener__(self))

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
                    clicked_handler=self.__calculate_statistics_handler__)
        self.__enabled_calculation_button__(False)

        self.__save_outcomes_button__ = CheckBoxWidget(buttons_composite,
                                    i18n_def="Save outcomes", enabled=False)

        #if parameter save_outcomes_fixed_state is not None
        #then it's equal to checked state of save outcomes button
        #and this state couldn't be change later by a user
        if self.params.save_outcomes_fixed_state:
            self.__save_outcomes_button__.setChecked(
                                        self.params.save_outcomes_fixed_state)

    def __calculate_statistics_handler__(self):
        if len(self.data_accessors) == 0:
            return

        self.main_data_accessor.prepareParametersContainer()
        #processing many data accessors objects:
        #self.data_accessors object contains many data_accessor objects which
        #have to be treated in the same way as self.main_data_accessor object,
        #that means they must have the same parameters
        for data_accessor in self.data_accessors:
            data_accessor.parameters_container = self.main_data_accessor.parameters_container # @IgnorePep8

        formatted_summary_statistics = []
        save_csv = self.__save_outcomes_button__.isChecked()
        check_level = CoreParameters.MEDIUM_CHECK_LEVEL if save_csv else CoreParameters.LOW_CHECK_LEVEL # @IgnorePep8

        pp_generator_progress_bar = PoincarePlotGeneratorProgressBar(self,
                self.data_accessors, label_text='Statistics calculation',
                check_level=check_level, save_csv=save_csv,
                formatted_summary_statistics=formatted_summary_statistics,
                output_file_listener=self.params.output_file_listener)
        pp_generator_progress_bar.start()
        if pp_generator_progress_bar.interrupted() == False and \
            len(formatted_summary_statistics) == 1:
            #summary statistics values are updated only in the case
            #of one data accessor object
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
        self.__enabled_calculation_button__(_checked)

        #only if this parameter is None save outcomes button's check state
        #could be changed
        if self.params.save_outcomes_fixed_state == None:
            self.__save_outcomes_button__.setEnabled(_checked)

    def getSelectedStatisticsClasses(self):
        return self.__statistics_widget__.getSelectedStatisticsClasses()

    def getSelectedSummaryStatisticsClasses(self):
        return self.__summary_statistics_widget__.getSelectedStatisticsClasses() # @IgnorePep8

    def __enabled_calculation_button__(self, _enabled):
        """
        method sets background color of 'Calculate statistics' button to red
        if the button is disabled foreground color is set up to brown
        otherwise to black
        """
        if _enabled == False:
            self.__calculate_button__.setStyleSheet("background-color: red; color: brown") # @IgnorePep8
        else:
            self.__calculate_button__.setStyleSheet("background-color: red; color: black") # @IgnorePep8
        self.__calculate_button__.setEnabled(_enabled)


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
                        PoincarePlotParameters.NAME, PoincarePlotParameters)
        #StatisticParameters.NAME, StatisticParameters)

        parameters.clearStatisticsClasses()
        parameters.statistics_classes = w.getSelectedStatisticsClasses()

        parameters.clearSummaryStatisticsClasses()
        parameters.summary_statistics_classes = \
                            w.getSelectedSummaryStatisticsClasses()
