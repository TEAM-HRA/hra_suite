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
    #this value is set up in __createModel__ method
    VALUE_COLUMN = 0

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
        self.__table__ = TableViewWidget(self,
            change_check_count_handler=self.params.change_selection_count_handler) # @IgnorePep8
        self.__table__.setSelectionMode(QAbstractItemView.MultiSelection)
        self.__table__.setSelectionBehavior(QAbstractItemView.SelectRows)

    def __createModel__(self):
        model = __StatisticsSelectionModel__(self)
        labels = QStringList(["Statistic", "Description", "Value"])
        StatisticsSelectionWidget.VALUE_COLUMN = labels.indexOf("Value")
        model.setNumValueColumn(StatisticsSelectionWidget.VALUE_COLUMN)
        model.setHorizontalHeaderLabels(labels)
        self.__table__.setModel(model)
        self.__table__.setColumnHidden(StatisticsSelectionWidget.VALUE_COLUMN,
                                       True)

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

        self.__statistics_classes__ = []

        for base_class in _statistics_base_classes:
            for subclass in get_subclasses(base_class):
                self.__statistics_classes__.append(subclass)

        #sort alphabetically
        cmp_stat = lambda x, y: cmp(x.__name__, y.__name__)
        self.__statistics_classes__ = sorted(self.__statistics_classes__,
                                             cmp_stat)

        for statistic_class in self.__statistics_classes__:
            check_column = QStandardItem('%s' % statistic_class.__name__)
            check_column.setCheckState(Qt.Unchecked)
            check_column.setCheckable(True)

            description_column = QStandardItem(str(statistic_class().description)) # @IgnorePep8

            value_column = QStandardItem('')

            model.appendRow([check_column, description_column, value_column])

    @property
    def statistics_classes(self):
        return self.__statistics_classes__

    def setStatisticsValues(self, values_map):
        """
        method to set up statistics values
        """
        #show value column
        self.__table__.setColumnHidden(StatisticsSelectionWidget.VALUE_COLUMN,
                                       False)
        for statistic_class in values_map:
            row = self.__statistics_classes__.index(statistic_class)
            self.__table__.model().setItem(row,
                            StatisticsSelectionWidget.VALUE_COLUMN,
                            QStandardItem(str(values_map[statistic_class])))


class __StatisticsSelectionModel__(QStandardItemModel):
    """
    custom model for StatisticsSelectionWidget
    """
    def __init__(self, parent):
        QStandardItemModel.__init__(self, parent=parent)
        self.__num_value_column__ = -1

    def setNumValueColumn(self, _num_value_column):
        self.__num_value_column__ = _num_value_column

    def data(self, _modelIndex, _role):
        #the third column (indexing starts from 0) is a value of statistic
        if _modelIndex.column() == self.__num_value_column__ and \
            _role == Qt.TextAlignmentRole:
            return Qt.AlignRight
        else:
            return super(__StatisticsSelectionModel__, self).data(_modelIndex,
                                                              _role)
