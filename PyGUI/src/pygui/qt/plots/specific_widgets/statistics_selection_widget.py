'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.introspection import get_subclasses
    from pycore.misc import Params
    from pymath.statistics.statistics import Asymmetry
    from pygui.qt.widgets.table_view_widget import TableViewWidget
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class StatisticsSelectionWidget(GroupBoxWidget):
    """
    widget which gives ability to select statistics
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Statistics')
        super(StatisticsSelectionWidget, self).__init__(parent, **params)

        self.params = Params(**params)
        if self.params.statistics_base_classes == None:
            self.params.statistics_base_classes = [Asymmetry]

        self.__createButtons__()
        self.__createTable__()
        self.__createModel__()
        self.__fillStatistics__(self.params.statistics_base_classes)

    def __createTable__(self):
        self.__table__ = TableViewWidget(self)
        self.__table__.setSelectionMode(QAbstractItemView.MultiSelection)
        self.__table__.setSelectionBehavior(QAbstractItemView.SelectRows)

    def __createModel__(self):
        model = QStandardItemModel(self)
        labels = QStringList(["Statistic", "Description"])
        model.setHorizontalHeaderLabels(labels)
        self.__table__.setModel(model)

    def __createButtons__(self):
        buttons_composite = CompositeWidget(self, layout=QHBoxLayout())
        PushButtonWidget(buttons_composite, i18n_def="Select all",
                    clicked_handler=self.__select_all_handler__)

        PushButtonWidget(buttons_composite, i18n_def="Unselect all",
                    clicked_handler=self.__unselect_all_handler__)

    def __select_all_handler__(self):
        self.__table__.changeCheckStatForAll(True)

    def __unselect_all_handler__(self):
        self.__table__.changeCheckStatForAll(False)

    def __fillStatistics__(self, _statistics_base_classes):
        model = self.__table__.model()
        model.removeRows(0, model.rowCount())

        statistics = {}
        for base_class in _statistics_base_classes:
            for subclass in get_subclasses(base_class):
                statistics[subclass.__name__] = subclass().description

        for name in sorted([statistic_name for statistic_name in statistics]):
            check_column = QStandardItem('%s' % name)
            check_column.setCheckState(Qt.Unchecked)
            check_column.setCheckable(True)

            model.appendRow([check_column,
                             QStandardItem(str(statistics[name]))])
