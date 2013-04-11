'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import is_empty
    from pycore.collections_utils import get_or_put
    from pycore.misc import Params
    from pymath.datasources import get_unique_annotations
    from pymath.datasources import ALL_ANNOTATIONS
    from pygui.qt.utils.widgets import ButtonGroupCommon
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.utils.windows import InformationWindow
    from pygui.qt.utils.widgets import PushButtonCommon
    from pygui.qt.utils.widgets import NumberEditCommon
    from pygui.qt.utils.widgets import LabelCommon
    from pygui.qt.utils.signals import BUTTON_CLICKED_SIGNAL
    from pymath.time_domain.poincare_plot.filters.annotation_filter import AnnotationFilter # @IgnorePep8
    from pymath.time_domain.poincare_plot.filters.square_filter import SquareFilter # @IgnorePep8
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
        #self.addItem("- Filters -")
        self.__annotation_filter__ = __AnnotationFilterWidget__(self,
                                    data_accessor=self.data_accessor)
        self.__square_filter__ = __SquareFilterWidget__(self,
                                    data_accessor=self.data_accessor)

        PushButtonCommon(self, i18n_def='Restore filters',
                        clicked_handler=self.__restore_handler__)

    def __restore_handler__(self):
        self.data_accessor.restore()
        self.__annotation_filter__.reset()
        self.__square_filter__.reset()


class __AnnotationFilterWidget__(GroupBoxCommon):
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QHBoxLayout())
        super(__AnnotationFilterWidget__, self).__init__(parent,
                                        i18n_def="Annotation filter", **params)
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        unique_annotations = get_unique_annotations(
                                            self.data_accessor.annotation)
        if is_empty(unique_annotations):
            self.setEnabled(False)
        else:
            self.__allCheckBox__ = CheckBoxCommon(self, i18n_def='ALL',
                                        clicked_handler=self.__all_handler__)

            self.__button_group__ = ButtonGroupCommon(self)

            for unique_annotation in unique_annotations:
                annotationCheckBox = CheckBoxCommon(self,
                                    i18n_def=str(unique_annotation))
                self.__button_group__.addButton(annotationCheckBox)
            self.__button_group__.setExclusive(False)
            self.__button_group__.connect(self.__button_group__,
                                          BUTTON_CLICKED_SIGNAL,
                                          self.__one_handler__)

            self.__button_apply__ = PushButtonCommon(self, i18n_def='Apply',
                                clicked_handler=self.__annotation_handler__)
            self.__button_apply__.setEnabled(False)

    def __annotation_handler__(self):
        __filter__(self.parent(), AnnotationFilter(), self.data_accessor,
                   self.__excluded_annotations__())

    def __excluded_annotations__(self):
        if self.__allCheckBox__.isChecked():
            self.setEnabled(False)
            self.__button_apply__.setEnabled(False)
            return ALL_ANNOTATIONS
        else:
            annotations = []
            for button in self.__button_group__.buttons():
                if button.isChecked():
                    annotations.append(int(button.text()))
                    button.setEnabled(False)
            if self.__button_group__.isAllChecked():
                self.setEnabled(False)
                self.__button_apply__.setEnabled(False)
            return annotations

    def __all_handler__(self):
        if self.__allCheckBox__.isChecked():
            self.__button_apply__.setEnabled(True)
            self.__button_group__.setAllChecked(False)
        else:
            self.__button_apply__.setEnabled(False)

    def __one_handler__(self, button):
        if button.isChecked():
            self.__allCheckBox__.setChecked(False)
            self.__button_apply__.setEnabled(True)
        else:
            if self.__button_group__.isAllUnchecked():
                self.__button_apply__.setEnabled(False)

    def setChecked(self, _check):
        self.__button_group__.setAllChecked(_check)
        self.__allCheckBox__.setChecked(_check)

    def setEnabled(self, _enabled):
        self.__button_group__.setEnabled(_enabled)
        self.__allCheckBox__.setEnabled(_enabled)

    def reset(self):
        self.setChecked(False)
        self.setEnabled(True)


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


class __SquareFilterWidget__(GroupBoxCommon):
    """
    graphical representation of a square filter
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QHBoxLayout())
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        i18n_def = "Square filter " + self.data_accessor.signal_unit.display_label # @IgnorePep8
        super(__SquareFilterWidget__, self).__init__(parent, i18n_def=i18n_def,
                                                     **params)

        self.__filter__ = SquareFilter()

        LabelCommon(self, i18n_def="Min value")
        self.__min_value__ = NumberEditCommon(self,
                                        text_handler=self.__min_handler__)
        LabelCommon(self, i18n_def="Max value")
        self.__max_value__ = NumberEditCommon(self,
                                        text_handler=self.__max_handler__)

        self.__button_apply__ = PushButtonCommon(self, i18n_def='Apply',
                                clicked_handler=self.__filter_handler__)
        self.reset()

    def __filter_handler__(self):
        __filter__(self.parent(), self.__filter__, self.data_accessor)

    def setEnabled(self, _enabled):
        self.__min_value__.setEnabled(_enabled)
        self.__max_value__.setEnabled(_enabled)

    def __min_handler__(self, text):
        self.__filter__.min_value = text
        self.__check_range__(self.__min_value__)

    def __max_handler__(self, text):
        self.__filter__.max_value = text
        self.__check_range__(self.__max_value__)

    def reset(self):
        self.setEnabled(True)
        self.__filter__.reset()
        self.__min_value__.setText(self.__filter__.min_value)
        self.__max_value__.setText(self.__filter__.max_value)

    def __check_range__(self, _widget):
        message = self.__filter__.check()
        if message == None:
            self.__button_apply__.setEnabled(True)
            _widget.setToolTip('')
            self.__button_apply__.setToolTip('')
            return True
        else:
            _widget.setToolTip(message)
            self.__button_apply__.setToolTip(message)
            self.__button_apply__.setEnabled(False)
            return False
