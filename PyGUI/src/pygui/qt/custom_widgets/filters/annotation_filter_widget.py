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
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.utils.widgets import PushButtonCommon
    from pygui.qt.utils.signals import BUTTON_CLICKED_SIGNAL
    from pymath.time_domain.poincare_plot.filters.annotation_filter import AnnotationFilter # @IgnorePep8
    from pygui.qt.custom_widgets.filters.filter_utils import run_filter
except ImportError as error:
    ImportErrorMessage(error, __name__)


class AnnotationFilterWidget(GroupBoxCommon):
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QHBoxLayout())
        super(AnnotationFilterWidget, self).__init__(parent,
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
        run_filter(self.parent(), AnnotationFilter(), self.data_accessor,
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
        self.__button_apply__.setEnabled(False)
