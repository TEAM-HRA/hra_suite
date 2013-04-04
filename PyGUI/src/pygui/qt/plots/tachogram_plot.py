'''
Created on 15-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.collections_utils import nvl
    from pycore.misc import Params
    from pycore.introspection import get_child_of_type
    from pycore.units import OrderUnit
    from pymath.datasources import FileDataSource
    from pymath.statistics.tachogram_statistics import calculate_tachogram_statistics # @IgnorePep8
    from pygui.qt.utils.dnd import CopyDragger
    from pygui.qt.utils.widgets import MainWindowCommon
    from pygui.qt.utils.widgets import LabelCommon
    from pygui.qt.utils.widgets import DockWidgetCommon
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import TableViewCommon
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.custom_widgets.tabwidget import TabWidgetCommon
    from pygui.qt.custom_widgets.units import TimeUnitsWidget
    from pygui.qt.plots.tachogram_plot_plot import TachogramPlotPlot
    from pygui.qt.plots.tachogram_plot_plot import STATISTIC_MIME_ID
    from pygui.qt.plots.tachogram_plot_plot import STATISTIC_CLASS_NAME_ID
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.utils.signals import TAB_WIDGET_ADDED_SIGNAL
    from pygui.qt.plots.plots_signals import CLOSE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import MAXIMIZE_TACHOGRAM_PLOT_SIGNAL
    from pygui.qt.plots.plots_signals import RESTORE_TACHOGRAM_PLOT_SIGNAL
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotManager(TabWidgetCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotManager, self).__init__(parent, **params)
        SignalDispatcher.addSignalSubscriber(self,
                                             CLOSE_TACHOGRAM_PLOT_SIGNAL,
                                             self.__closeTachogramPlotTab__)

    def addTachogramPlot(self, file_specification, allow_duplication=False,
                         first_focus=False):
        if file_specification:
            object_name = self.__getObjectName__(file_specification)
            if allow_duplication == False and self.tabExists(object_name):
                return
            tab = self.__createTachogramTab__(file_specification, object_name)
            if tab and first_focus:
                self.setTabFocus(tab)
            return tab

    def createInitialPlot(self):
        self.__initial_tab__ = MainWindowCommon(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label = LabelCommon(self.__initial_tab__,
                            i18n="tachogram.initial.page.label",
                            i18n_def="Tachogram area",
                            sizePolicy=sizePolicy,
                            not_add_widget_to_parent_layout=True)
        self.__initial_tab__.setCentralWidget(label)
        self.addTab(self.__initial_tab__, 'Welcome')
        self.markTabAsNotClose(self.__initial_tab__)

    def __createTachogramTab__(self, file_specification, object_name):
        tachogramTabWidget = TachogramPlotWindow(self,
                                    file_specification=file_specification)
        tachogramTabWidget.setObjectName(object_name)
        self.addTab(tachogramTabWidget,
                    self.getNextTitle(file_specification.filename))
        SignalDispatcher.broadcastSignal(TAB_WIDGET_ADDED_SIGNAL)
        return tachogramTabWidget

    def __getObjectName__(self, file_specification):
        return ".".join([file_specification.pathname,
                         file_specification.filename])

    def __closeTachogramPlotTab__(self, _tachogram_plot_tab):
        idx = self.indexOf(_tachogram_plot_tab)
        self.removeTab(idx)


class TachogramPlotWindow(MainWindowCommon):
    def __init__(self, parent, **params):
        super(TachogramPlotWindow, self).__init__(parent, **params)
        self.params = Params(**params)

        self.addToolBar(OperationalToolBarWidget(self))

        self.tachogramPlot = TachogramPlotPlot(self,
            file_specification=self.params.file_specification,
            show_tachogram_plot_settings_handler=self.__show_tachogram_plot_settings_handler__,   # @IgnorePep8
            show_tachogram_plot_statistics_handler=self.__show_tachogram_plot_statistics_handler__)  # @IgnorePep8
        self.setCentralWidget(self.tachogramPlot)

    def toolbar_maximum_handler(self):
        SignalDispatcher.broadcastSignal(MAXIMIZE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_restore_handler(self):
        SignalDispatcher.broadcastSignal(RESTORE_TACHOGRAM_PLOT_SIGNAL)

    def toolbar_close_handler(self):
        SignalDispatcher.broadcastSignal(CLOSE_TACHOGRAM_PLOT_SIGNAL, self)

    def __show_tachogram_plot_settings_handler__(self, _x_unit):
        tachogram_plot_dock_widget = get_child_of_type(self,
                                             TachogramPlotSettingsDockWidget)
        if tachogram_plot_dock_widget == None:
            tachogram_plot_dock_widget = TachogramPlotSettingsDockWidget(self,
                            x_unit=_x_unit,
                            change_unit_handler=self.__change_unit_handler__)
        tachogram_plot_dock_widget.show()

    def __show_tachogram_plot_statistics_handler__(self):
        dock_widget = get_child_of_type(self, TachogramPlotStatisticsDockWidget) # @IgnorePep8
        if dock_widget == None:
            dock_widget = TachogramPlotStatisticsDockWidget(self,
                            file_specification=self.params.file_specification)
        dock_widget.show()

    def __change_unit_handler__(self, _unit):
        self.tachogramPlot.changeXUnit(_unit)
#        statusbar = StatusBarCommon(self.__initial_tab__)
#        self.__initial_tab__.setStatusBar(statusbar)
#        statusLabel = LabelCommon(statusbar,
#                    i18n_def="STATUS",
#                    add_widget_to_parent=True)
#


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


class TachogramStatisticsWidget(TableViewCommon):
    """
    a widget to display basic tachogram's statistics
    """
    def __init__(self, parent, **params):
        TableViewCommon.__init__(self, parent, **params)
        self.__dragger__ = CopyDragger(self, STATISTIC_MIME_ID, drag_only=True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setColumnHidden(0, True)  # "classname" columns is hidden
        self.__createModel__()

    def __createModel__(self):
        model = TachogramStatisticsModel(self)
        labels = QStringList(["class_name", "Statistic", "Value"])
        model.setHorizontalHeaderLabels(labels)
        self.setModel(model)

    def setTachogramStatistics(self, _statistics):
        model = self.model()
        model.removeRows(0, model.rowCount())
        values = _statistics[0]
        descriptions = _statistics[1]
        self.class_names = sorted([name for name in values])
        for name in sorted([name for name in self.class_names]):
            model.appendRow([QStandardItem(str(name)),
                             QStandardItem(str(descriptions[name])),
                             QStandardItem(str(values[name]))])

    def startDrag(self, dropActions):
        row = self.model().itemFromIndex(self.currentIndex()).row()
        self.__dragger__.clear()
        self.__dragger__.dragObject(STATISTIC_CLASS_NAME_ID,
                                    self.class_names[row])
        self.__dragger__.startDrag()


class TachogramStatisticsModel(QStandardItemModel):
    def __init__(self, parent):
        QStandardItemModel.__init__(self, parent=parent)

    def data(self, _modelIndex, _role):
        #the first column (with index 0) is a name of statistic
        if _modelIndex.column() == 1 and _role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        else:
            return super(TachogramStatisticsModel, self).data(_modelIndex,
                                                              _role)


class TachogramPlotStatisticsDockWidget(DockWidgetCommon):
    """
    a dock widget for tachogram plot statistics
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
        super(TachogramPlotStatisticsDockWidget, self).__init__(parent,
                        title=params.get('title', 'Tachogram plot statistics'),
                        **params)
        file_data_source_params = self.params.file_specification._asdict()
        file_data_source = FileDataSource(**file_data_source_params)
        data_vector = file_data_source.getData()

        self.setObjectName("TachogramPlotStatisticsDockWidget")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea |
                             Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        layout = QVBoxLayout()
        layout.setMargin(0)  # no margin for internal layout
        self.dockComposite = CompositeCommon(self, layout=layout,
                                        not_add_widget_to_parent_layout=True)
        self.__createStatisticsWidget__(QVBoxLayout(), data_vector)

        self.setWidget(self.dockComposite)
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

    def __createStatisticsWidget__(self, _layout, _data_vector):
        self.statisticsWidget = TachogramStatisticsWidget(self.dockComposite,
                                                          layout=_layout)
        statistics = calculate_tachogram_statistics(signal=_data_vector.signal,
                                            annotation=_data_vector.annotation)
        self.statisticsWidget.setTachogramStatistics(statistics)
