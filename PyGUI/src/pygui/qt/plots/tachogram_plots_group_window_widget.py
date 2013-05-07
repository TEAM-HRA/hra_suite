'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.utils.windows import InformationWindow
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.custom_widgets.toolbars import CloseToolButton
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.main_window_widget import MainWindowWidget
    from pygui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.specific_widgets.poincare_toolbar_widget import PoincareToolBarWidget # @IgnorePep8
    from pygui.qt.plots.poincare_plot_settings_dock_widget import PoincarePlotSettingsDockWidget # @IgnorePep8
    from pygui.qt.plots.outcome_files_tracker_dock_widget import OutcomeFilesTrackerDockWidget # @IgnorePep8
    from pygui.qt.custom_widgets.file_specification_to_data_accessor_progress_bar import FileSpecificationToDataAccessorProgressBar # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotsGroupWindowWidget(MainWindowWidget):
    """
    initial tachogram plot window used to take operations
    on the whole group of tachogram plots
    """
    def __init__(self, parent, **params):
        super(TachogramPlotsGroupWindowWidget, self).__init__(parent, **params)
        self.params = Params(**params)

        self.addToolBar(OperationalToolBarWidget(self,
                                        excluded_buttons=[CloseToolButton]))
        self.addToolBar(PoincareToolBarWidget(self))

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        composite = CompositeWidget(self,
                            sizePolicy=sizePolicy,
                            not_add_widget_to_parent_layout=True)
        self.setCentralWidget(composite)
        self.__file_specifications__ = []
        self.__selected_files_specifications_handler__ = None

#        self.tachogramPlot = __TachogramPlot__(self,
#                        file_specification=_files_specifications[0])
#        self.setCentralWidget(self.tachogramPlot)

    def toolbar_maximum_handler(self):
        SignalDispatcher.broadcastSignal(MAXIMIZE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_restore_handler(self):
        SignalDispatcher.broadcastSignal(RESTORE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_close_handler(self):
        SignalDispatcher.broadcastSignal(CLOSE_TACHOGRAM_PLOT_SIGNAL, self)

    def addFileSpecification(self, _file_specification):
        if self.__file_specifications__.count(_file_specification) == 0:
            self.__file_specifications__.append(_file_specification)

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

            #create data accessor objects based on file specification objects
            #to inform a user about progression special kind of progress bar
            #is used
            data_accessor_progress_bar = FileSpecificationToDataAccessorProgressBar( # @IgnorePep8
                                            self, self.__file_specifications__)
            data_accessor_progress_bar.start()
            data_accessors = data_accessor_progress_bar.data_accessors

            #the first element is reference data accessor object
            data_accessor = data_accessors[0]
            #remaining elements (if any) constitute data accessors group
            data_accessors_group = data_accessors[1:] if len(data_accessors) > 1 else None # @IgnorePep8

            self.__poincare_settings__ = PoincarePlotSettingsDockWidget(
                        self, data_accessor=data_accessor,
                        data_accessors_group=data_accessors_group,
                        output_file_listener=self.__output_file_listener__
                        )
        self.__poincare_settings__.show()

    def __output_file_listener__(self, _filename):
        if not hasattr(self, '__outcome_files_tracker__'):
            self.__outcome_files_tracker__ = OutcomeFilesTrackerDockWidget(
                                                                        self)
        self.__outcome_files_tracker__.show()
        self.__outcome_files_tracker__.appendFile(_filename)

    def setSelectedFilesSpecificationsHandler(self,
                                    _selected_files_specifications_handler):
        self.__selected_files_specifications_handler__ = \
                                    _selected_files_specifications_handler
#class __TachogramPlot__(CompositeWidget):
#    """
#    this class represents core of the tachogram plot that is a plot itself
#    """
#    def __init__(self, parent, **params):
#        super(__TachogramPlot__, self).__init__(parent,
#                                        not_add_widget_to_parent_layout=True)
#        self.params = Params(**params)
#        file_data_source_params = self.params.file_specification._asdict()
#        self.signal_unit = get_unit_by_class_name(
#                        file_data_source_params.get('signal_unit_class_name'))
#        file_data_source = FileDataSource(**file_data_source_params)
#        layout = QVBoxLayout()
#        self.setLayout(layout)
#        data = file_data_source.getData()
#        data_accessor = DataVectorAccessor(data)
#        data_accessor.source_name = file_data_source.source_filename
#        data_accessor.changeXSignalUnit(self, OrderUnit)
#        self.canvas = TachogramPlotCanvas(self, data_accessor=data_accessor)
#        layout.addWidget(self.canvas)
#        self.navigation_toolbar = TachogramPlotNavigationToolbar(
#                                                self, self.canvas,
#                                                dock_parent=parent,
#                                                data_accessor=data_accessor)
#        layout.addWidget(self.navigation_toolbar)
