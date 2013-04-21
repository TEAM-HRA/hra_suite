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
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.custom_widgets.filters.square_filter_widget import SquareFilterWidget # @IgnorePep8
    from pygui.qt.custom_widgets.filters.common_annotation_filter_widget import CommonAnnotationFilterWidget  # @IgnorePep8
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
        self.data_accessor.addListener(self,
                                __FilterActivatedDataVectorListener__(self))

        filtersGroup = GroupBoxCommon(self, layout=QVBoxLayout(),
                                      i18n_def=params.get('title', 'Filters'))
        annotation_widget_class = params.get('annotation_widget_class', False)
        if annotation_widget_class:
            self.__annotation_filter__ = annotation_widget_class(
                                filtersGroup, data_accessor=self.data_accessor)
        else:
            self.__annotation_filter__ = CommonAnnotationFilterWidget(
                                filtersGroup, data_accessor=self.data_accessor)

        use_apply_button = params.get('use_apply_button', False)
        self.__square_filter__ = SquareFilterWidget(filtersGroup,
                                    data_accessor=self.data_accessor,
                                    use_apply_button=use_apply_button)

        if params.get('restore_button', False):
            self.__restore_button__ = PushButtonWidget(filtersGroup,
                                     i18n_def='Back to unfiltered data',
                                     clicked_handler=self.__restore_handler__,
                                     enabled=False)

    def __restore_handler__(self):
        self.data_accessor.restore(remove_filter_names=True)
        self.__annotation_filter__.reset()
        self.__square_filter__.reset()
        if hasattr(self, '__restore_button__'):
            self.__restore_button__.setEnabled(False)

    def enableRestoreButton(self):
        if hasattr(self, '__restore_button__'):
            self.__restore_button__.setEnabled(True)


class __FilterActivatedDataVectorListener__(DataVectorListener):
    """
    this class is run when any filter is activated
    """
    def __init__(self, _filter_widget):
        self.__filter_widget__ = _filter_widget

    def changeSignal(self, _signal, **params):
        self.__filter_widget__.enableRestoreButton()

    def changeAnnotation(self, _annotation, **params):
        self.__filter_widget__.enableRestoreButton()
