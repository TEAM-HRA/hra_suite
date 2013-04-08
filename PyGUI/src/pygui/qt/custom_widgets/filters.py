'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import is_none_or_zero_length
    from pycore.collections_utils import get_or_put
    from pycore.misc import Params
    from pymath.datasources import get_unique_annotations
    from pymath.datasources import ALL_ANNOTATIONS
    from pymath.time_domain.poincare_plot.filters import AnnotationFilter
    from pygui.qt.utils.widgets import ButtonGroupCommon
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.utils.windows import InformationWindow
    from pygui.qt.utils.widgets import PushButtonCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


class FiltersWidget(CompositeCommon):
    """
    a composite widget to choose a filtering method based on
    subclasses of Filter class
    """
    def __init__(self, parent, **params):
        super(FiltersWidget, self).__init__(parent, **params)
        data_accessor = self.params.data_accessor  # alias
        #self.addItem("- Filters -")
        __AnnotationFilterWidget__(self, data_accessor=data_accessor)


class __AnnotationFilterWidget__(GroupBoxCommon):
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QHBoxLayout())
        super(__AnnotationFilterWidget__, self).__init__(parent,
                                        i18n_def="Annotation filter", **params)
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        unique_annotations = get_unique_annotations(
                                            self.data_accessor.annotation)
        if is_none_or_zero_length(unique_annotations):
            self.setEnabled(False)
        else:
            button_group = ButtonGroupCommon(self)

            self.__allCheckBox__ = CheckBoxCommon(self, i18n_def='ALL')
            self.__allCheckBox__.setChecked(True)
            button_group.addButton(self.__allCheckBox__)

            for unique_annotation in unique_annotations:
                annotationCheckBox = CheckBoxCommon(self,
                                    i18n_def=str(unique_annotation))
                button_group.addButton(annotationCheckBox)

        PushButtonCommon(parent, i18n_def='Apply',
                        clicked_handler=self.__annotation_handler__)

    def __annotation_handler__(self):
        __filter__(self.parent(), AnnotationFilter(), self.data_accessor,
                   self.__excluded_annotations__())

    def __excluded_annotations__(self):
        return ALL_ANNOTATIONS


def __filter__(parent, _filter, _data_accessor, _excluded_annotations=None):
    """
    function run filter
    """
    if _excluded_annotations:
        message = _filter.check(_data_accessor.data_vector,
                                _excluded_annotations)
    else:
        message = _filter.check(_data_accessor.data_vector)
    if not message == None:
        InformationWindow(parent, message=message)
        return
    if _excluded_annotations:
        filtered_data = _filter.filter(_data_accessor.data_vector,
                                       _excluded_annotations)
    else:
        filtered_data = _filter.filter(_data_accessor.data_vector)
    _data_accessor.changeSignal(parent, filtered_data.signal)
    _data_accessor.changeAnnotation(parent, filtered_data.annotation)
