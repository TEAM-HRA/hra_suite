'''
Created on 04-04-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_gui.qt.utils.signals import SignalDispatcher
    from hra_gui.qt.utils.settings import set_temporary_settings_id
    from hra_gui.qt.utils.specials import widgets_have_the_same_parent
    from hra_gui.qt.utils.windows import InformationWindow
    from hra_gui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from hra_gui.qt.custom_widgets.toolbars import CloseToolButton
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.main_window_widget import MainWindowWidget
    from hra_gui.qt.plots.objects_names import TACHOGRAM_PLOT_TAB_ITEM_WIDGET_OBJECT_NAME # @IgnorePep8
    from hra_gui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from hra_gui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from hra_gui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
    from hra_gui.qt.plots.specific_widgets.poincare_toolbar_widget import PoincareToolBarWidget # @IgnorePep8
    from hra_gui.qt.docks.poincare_plot_settings_dock_widget import PoincarePlotSettingsDockWidget # @IgnorePep8
    from hra_gui.qt.docks.outcome_files_tracker_dock_widget import OutcomeFilesTrackerDockWidget # @IgnorePep8
    from hra_gui.qt.plots.specific_widgets.poincare_plot_datasources_table_widget import PoincarePlotDatasourcesTableWidget # @IgnorePep8
    from hra_gui.qt.custom_widgets.files_specifications_to_data_accessors_group_converter import FilesSpecificationsToDataAccessorsGroupConverter  # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotSummaryCompositeWidget(MainWindowWidget):
    """
    initial tachogram plot window used to take operations
    on the whole group of tachogram plots
    """
    def __init__(self, parent, **params):
        super(TachogramPlotSummaryCompositeWidget, self).__init__(parent,
                                                                 **params)
        set_temporary_settings_id(self)
        self.params = Params(**params)

        self.addToolBar(OperationalToolBarWidget(self,
                                        excluded_buttons=[CloseToolButton]))
        self.addToolBar(PoincareToolBarWidget(self, reload_button=True))

        self.__central_widget__ = CompositeWidget(self,
                            not_add_widget_to_parent_layout=True)
        layout = QVBoxLayout()
        self.__central_widget__.setLayout(layout)
        self.setCentralWidget(self.__central_widget__)
        self.__file_specifications__ = []
        self.__selected_files_specifications_handler__ = None
        SignalDispatcher.addSignalSubscriber(self, CLOSE_TACHOGRAM_PLOT_SIGNAL,
                                            self.__removeFileSpecification__)

    def toolbar_maximum_handler(self):
        SignalDispatcher.broadcastSignal(MAXIMIZE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_restore_handler(self):
        SignalDispatcher.broadcastSignal(RESTORE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_close_handler(self):
        SignalDispatcher.broadcastSignal(CLOSE_TACHOGRAM_PLOT_SIGNAL, self)

    def addFileSpecification(self, _file_specification):
        if self.__file_specifications__.count(_file_specification) == 0:
            self.__file_specifications__.append(_file_specification)

    def reload_poincare_settings_handler(self):
        """
        handler call by PoincareToolBarWidget toolbar
        reloads poincare plot settings widget
        """
        if hasattr(self, '__poincare_settings__'):
            self.removeDockWidget(self.__poincare_settings__)
            self.layout().removeWidget(self.__poincare_settings__)
            self.__poincare_settings__.deleteLater()
            delattr(self, '__poincare_settings__')

        if hasattr(self, '__poincare_datasources_table__'):
            self.layout().removeWidget(self.__poincare_datasources_table__)
            self.__poincare_datasources_table__.deleteLater()
            delattr(self, '__poincare_datasources_table__')

        self.show_poincare_settings_handler()

    def show_poincare_settings_handler(self):
        """
        handler call by PoincareToolBarWidget toolbar
        """

        if self.__selected_files_specifications_handler__:
            selected_files_specifications = \
                        self.__selected_files_specifications_handler__()
            if len(selected_files_specifications) > 0:
                for file_specification in selected_files_specifications:
                    self.addFileSpecification(file_specification)

        if len(self.__file_specifications__) == 0:
            InformationWindow(message='No data sources selected !')
            return
        if not hasattr(self, '__poincare_settings__'):

            #to convert data accessor objects based on file specification
            #objects to inform a user about progression special kind of
            #progress bar is used
            data_accessors_group_converter = \
                FilesSpecificationsToDataAccessorsGroupConverter(
                                            self, self.__file_specifications__)

            data_vectors_accessor_group = \
                data_accessors_group_converter.data_vectors_accessors_group

            self.__poincare_settings__ = PoincarePlotSettingsDockWidget(
                    self,
                    data_vectors_accessor_group=data_vectors_accessor_group,
                    output_file_listener=self.__output_file_listener__,
                    #save outcomes button in PoincarePlotSettingsDockWidget
                    #have to be in fixed check state
                    save_outcomes_fixed_state=True)
        self.__poincare_settings__.show()

        if not hasattr(self, '__poincare_datasources_table__'):
            self.__poincare_datasources_table__ = \
                    PoincarePlotDatasourcesTableWidget(self.__central_widget__,
                        data_accessors=data_vectors_accessor_group.data_vectors_accessors) # @IgnorePep8
        self.__poincare_datasources_table__.show()

    def __output_file_listener__(self, _filename):
        if not hasattr(self, '__outcome_files_tracker__'):
            self.__outcome_files_tracker__ = OutcomeFilesTrackerDockWidget(
                                                                        self)
        self.__outcome_files_tracker__.show()
        self.__outcome_files_tracker__.appendFile(_filename)

        if hasattr(self, '__poincare_datasources_table__'):
            self.__poincare_datasources_table__.checkMarkFile(_filename)

    def setSelectedFilesSpecificationsHandler(self,
                                    _selected_files_specifications_handler):
        self.__selected_files_specifications_handler__ = \
                                    _selected_files_specifications_handler

    def __removeFileSpecification__(self, _tachogram_plot_tab):
        """
        method is invoked when tachogram plot is closed to remove
        corresponding position from self.__file_specifications__
        """
        if widgets_have_the_same_parent(self, _tachogram_plot_tab,
                                 TACHOGRAM_PLOT_TAB_ITEM_WIDGET_OBJECT_NAME):
            if self.__file_specifications__.count(
                            _tachogram_plot_tab.file_specification) > 0:
                del self.__file_specifications__[
                            self.__file_specifications__.index(
                                _tachogram_plot_tab.file_specification)]
