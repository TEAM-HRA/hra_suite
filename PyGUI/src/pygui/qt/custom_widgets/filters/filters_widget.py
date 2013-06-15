'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.collections_utils import get_or_put
    from pymath.model.data_vector_listener import DataVectorListener
    from pymath.time_domain.poincare_plot.filters.filter_parameters import FilterParameters # @IgnorePep8    
    from pygui.qt.utils.settings import temporarySettingsDecorator
    from pygui.qt.utils.settings import temporarySetterDecorator
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
    from pygui.qt.custom_widgets.filters.square_filter_widget import SquareFilterWidget # @IgnorePep8
    from pygui.qt.custom_widgets.filters.common_annotation_filter_widget import CommonAnnotationFilterWidget  # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class FiltersWidget(CompositeWidget):
    """
    a composite widget to choose a filtering method based on
    subclasses of Filter class
    """
    @temporarySettingsDecorator()
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        super(FiltersWidget, self).__init__(parent, **params)
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        if self.params.use_apply_button == True:
            self.data_accessor.addListener(self,
                                __FilterActivatedDataVectorListener__(self))

        filtersGroup = GroupBoxWidget(self, layout=QVBoxLayout(),
                                      i18n_def=params.get('title', 'Filters'))
        annotation_widget_class = params.get('annotation_widget_class', False)
        if annotation_widget_class:
            self.__annotation_filter__ = annotation_widget_class(
                                filtersGroup, data_accessor=self.data_accessor)
        else:
            self.__annotation_filter__ = CommonAnnotationFilterWidget(
                                filtersGroup, data_accessor=self.data_accessor)

        self.__square_filter__ = SquareFilterWidget(filtersGroup,
                                data_accessor=self.data_accessor,
                                use_apply_button=self.params.use_apply_button)

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

    def getSquareFilterParams(self):
        return self.__square_filter__.getSquareFilterParams()

    @temporarySetterDecorator(name='square_filter_params',
                              _conv=QVariant.toPyObject,
                              _getter_handler=getSquareFilterParams)
    def setSquareFilterParams(self, square_filter_params):
        self.__square_filter__.setSquareFilterParams(square_filter_params)

    def getAnnotationFilterParams(self):
        return self.__annotation_filter__.getAnnotationFilterParams()

    @temporarySetterDecorator(name='annotation_filter_params',
                              _conv=QVariant.toPyObject,
                              _getter_handler=getAnnotationFilterParams)
    def setAnnotationFilterParams(self, annotation_filter_params):
        self.__annotation_filter__.setAnnotationFilterParams(
                                                annotation_filter_params)


class __FilterActivatedDataVectorListener__(DataVectorListener):
    """
    this class is run when any filter is activated
    """
    def __init__(self, _filters_widget):
        self.__filters_widget__ = _filters_widget

    def changeSignal(self, _signal, **params):
        self.__filters_widget__.enableRestoreButton()

    def changeAnnotation(self, _annotation, **params):
        self.__filters_widget__.enableRestoreButton()

    def prepareParameters(self, data_vector_accessor):
        container = data_vector_accessor.parameters_container
        filter_parameters = container.getParametersObject(
                                    FilterParameters.NAME, FilterParameters)

        w = self.__filters_widget__  # alias
        filter_parameters.clearFilters()
        if w.__annotation_filter__.useFilter():
            filter_parameters.addFilter(w.__annotation_filter__.getFilter())

        if w.__square_filter__.useFilter():
            filter_parameters.addFilter(w.__square_filter__.getFilter())
