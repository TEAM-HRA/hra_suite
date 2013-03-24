'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
from pygui.qt.utils.windows import InformationWindow
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pymath.datasources import DataVector
    from pymath.time_domain.poincare_plot.filters import DataVectorFilter
    from pycore.introspection import get_subclasses
    from pygui.qt.utils.widgets import ComboBoxCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


class FiltersWidget(ComboBoxCommon):
    """
    a combo box widget to choose a filtering method based on
    subclasses of DataVectorFilter class
    """
    def __init__(self, parent, _signal, _annotation, **params):
        #remember a filter handler as inner member
        self.__clicked_handler__ = None if params == None else \
                                    params.get('clicked_handler', None)
        #replace clicked_handler into __filter_clicked_handler__
        #because a need of use of filtering functionality
        params['clicked_handler'] = self.__filter_clicked_handler__
        super(FiltersWidget, self).__init__(parent, **params)
        self.__signal0__ = _signal
        self.__annotation0__ = _annotation
        self.__signal__ = self.__signal0__
        self.__annotation__ = self.__annotation0__
        self.__last_position__ = None
        self.addItem("- Filters -")
        for idx, filter_class in enumerate(get_subclasses(DataVectorFilter), 1): # @IgnorePep8
            filter_name = filter_class.__name__
            self.addItem(filter_name)
            #store class of filter in item data member
            self.setItemData(idx, QVariant(filter_class),
                                              Qt.UserRole)

    def __filter_clicked_handler__(self, position):
        if self.__last_position__ == None:
            self.__last_position__ = position
        if position == self.__last_position__:
            return
        itemData = self.itemData(position, Qt.UserRole)
        if not itemData == None:
            filter_class = itemData.toPyObject()
            filter_object = filter_class()

            filter_data = DataVector(signal=self.__signal__,
                                     annotation=self.__annotation__)
            #check if filtering has any sense
            message = filter_object.check(filter_data)
            if not message == None:
                InformationWindow(self.parent(), message=message)
                self.setCurrentIndex(self.__last_position__)
                return
            #filtering data
            filtered_data_vector = filter_object.filter(filter_data)

            self.__signal__ = filtered_data_vector.signal
            self.__annotation__ = filtered_data_vector.annotation
        else:
            #restore original values
            self.__signal__ = self.__signal0__
            self.__annotation__ = self.__annotation0__
        if self.__clicked_handler__:
            self.__clicked_handler__(self.__signal__, self.__annotation__)
        self.__last_position__ = position
