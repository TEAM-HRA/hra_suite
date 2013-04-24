'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.misc import Params
    from pymath.model.data_vector_listener import DataVectorListener
    from pymath.statistics.tachogram_statistics import calculate_tachogram_statistics  # @IgnorePep8
    from pygui.qt.utils.dnd import CopyDragger
    from pygui.qt.widgets.dock_widget_widget import DockWidgetWidget
    from pygui.qt.widgets.table_view_widget import TableViewWidget
    from pygui.qt.plots.tachogram_plot_const import STATISTIC_MIME_ID
    from pygui.qt.plots.tachogram_plot_const import STATISTIC_CLASS_NAME_ID
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotStatisticsDockWidget(DockWidgetWidget):
    """
    a dock widget for tachogram plot statistics
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
        super(TachogramPlotStatisticsDockWidget, self).__init__(parent,
                        title=params.get('title', 'Tachogram plot statistics'),
                        **params)
        self.data_accessor = self.params.data_accessor  # alias
        self.data_accessor.addListener(self,
                            __TachogramStatisticsDataVectorListener__(self))
        self.__createStatisticsWidget__(QVBoxLayout())
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

    def __createStatisticsWidget__(self, _layout):
        self.statisticsWidget = TachogramStatisticsWidget(self.dockComposite,
                                                          layout=_layout)
        self.fillStatisticsWidget()

    def fillStatisticsWidget(self):
        statistics = calculate_tachogram_statistics(
                                            signal=self.data_accessor.signal,
                                    annotation=self.data_accessor.annotation)
        self.statisticsWidget.setTachogramStatistics(statistics)


class TachogramStatisticsWidget(TableViewWidget):
    """
    a widget to display basic tachogram's statistics
    """
    def __init__(self, parent, **params):
        TableViewWidget.__init__(self, parent, **params)
        self.__dragger__ = CopyDragger(self, STATISTIC_MIME_ID, drag_only=True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
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
        self.setColumnHidden(0, True)  # "class_name" is a hidden column

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
        #the third column (indexing starts from 0) is a value of statistic
        if _modelIndex.column() == 2 and _role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        else:
            return super(TachogramStatisticsModel, self).data(_modelIndex,
                                                              _role)


class __TachogramStatisticsDataVectorListener__(DataVectorListener):
    """
    class used to recalculate tachogram statistics for tachogram
    statistics widget when signal or annotation data is changing
    """
    def __init__(self, _dock_widget):
        self.__dock_widget__ = _dock_widget

    def changeSignal(self, _signal, **params):
        self.__dock_widget__.fillStatisticsWidget()

    def changeAnnotation(self, _annotation, **params):
        self.__dock_widget__.fillStatisticsWidget()
