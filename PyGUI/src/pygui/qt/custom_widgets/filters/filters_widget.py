'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pymath.datasources import DataVectorListener
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import PushButtonCommon
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.custom_widgets.filters.annotation_filter_widget import AnnotationFilterWidget # @IgnorePep8
    from pygui.qt.custom_widgets.filters.square_filter_widget import SquareFilterWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class FiltersWidget(CompositeCommon):
    """
    a composite widget to choose a filtering method based on
    subclasses of Filter class
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        super(FiltersWidget, self).__init__(parent, **params)
        self.data_accessor = self.params.data_accessor  # alias
        self.data_accessor.addListener(self, __FilterActivatedDataVectorListener__(self)) # @IgnorePep8        

        filtersGroup = GroupBoxCommon(self, layout=QVBoxLayout(),
                                      i18n_def='Filters')
        self.__annotation_filter__ = AnnotationFilterWidget(filtersGroup,
                                    data_accessor=self.data_accessor)
        self.__square_filter__ = SquareFilterWidget(filtersGroup,
                                    data_accessor=self.data_accessor)

        self.__restore_button__ = PushButtonCommon(filtersGroup,
                                     i18n_def='Back to unfiltered data',
                                     clicked_handler=self.__restore_handler__,
                                     enabled=False)

    def __restore_handler__(self):
        self.data_accessor.restore()
        self.__annotation_filter__.reset()
        self.__square_filter__.reset()
        self.__restore_button__.setEnabled(False)

    def enableRestoreButton(self):
        self.__restore_button__.setEnabled(True)


class __FilterActivatedDataVectorListener__(DataVectorListener):
    """
    this class is run when any filter is activated
    """
    def __init__(self, _filter_widget):
        self.__filter_widget__ = _filter_widget

    def changeSignal(self, _signal):
        self.__filter_widget__.enableRestoreButton()

    def changeAnnotation(self, _annotation):
        self.__filter_widget__.enableRestoreButton()
