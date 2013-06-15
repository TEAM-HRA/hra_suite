'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import collections
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import is_empty
    from pycore.collections_utils import get_or_put
    from pycore.misc import Params
    from pymath.model.utils import get_unique_annotations
    from pymath.model.utils import ALL_ANNOTATIONS
    from pymath.time_domain.poincare_plot.filters.annotation_filter import AnnotationFilter # @IgnorePep8
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
    from pygui.qt.utils.signals import BUTTON_CLICKED_SIGNAL
    from pygui.qt.widgets.button_group_widget import ButtonGroupWidget
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)

#a tuple to collect all parameters of annotation filter widget in one structure
AnnotationFilterParams = collections.namedtuple('AnnotationFilterParams',
                            ['annotations', 'all_annotations', 'use_filter'])


class CommonAnnotationFilterWidget(GroupBoxWidget):
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QHBoxLayout())
        super(CommonAnnotationFilterWidget, self).__init__(parent, **params)
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        self.__filter__ = AnnotationFilter()
        self.__createAnnotationButtons__()
        self.createActionButton()
        self.__activateActionButton__(False)

    @property
    def action_button(self):
        pass

    @property
    def excluded_annotations(self):
        annotations = []
        for button in self.__button_group__.buttons():
            if button.isChecked():
                if button == self.__all_button__:
                    return ALL_ANNOTATIONS
                annotations.append(int(button.text()))
        return annotations

    def setEnabledAnnotations(self, _annotations):
        for button in self.__button_group__.buttons():
            if button == self.__all_button__:
                button.setEnabled(ALL_ANNOTATIONS == _annotations)
            elif ALL_ANNOTATIONS == _annotations or \
                int(button.text()) in _annotations:
                button.setEnabled(True)
            else:
                button.setEnabled(False)

    def setDisabledAnnotations(self, _annotations):
        for button in self.__button_group__.buttons():
            if button == self.__all_button__:
                button.setEnabled(not ALL_ANNOTATIONS == _annotations)
            elif ALL_ANNOTATIONS == _annotations or \
                int(button.text()) in _annotations:
                button.setEnabled(False)

    def disableIfAllChecked(self):
        for button in self.__button_group__.buttons():
            if not button == self.__all_button__ and not button.isChecked():
                return
        self.__all_button__.setEnabled(False)

    def reset(self):
        self.__button_group__.setEnabled(True)
        self.__button_group__.setAllChecked(False)
        self.__activateActionButton__(False)

    @property
    def use_filter(self):
        return self.__button_group__.isAnyChecked()

    @property
    def annotation_filter(self):
        return self.__filter__

    def set_title(self, empty):
        if empty:
            self.setTitle("Annotation filter [NOT ACTIVE - data already filtered]") # @IgnorePep8
            self.setEnabled(False)
        else:
            self.setTitle("Annotation filter")
            self.setEnabled(True)

    @property
    def buttons_count(self):
        return len(self.__button_group__.buttons())

    def setUncheckNotAnnotations(self, _annotations):
        for button in self.__button_group__.buttons():
            if button == self.__all_button__:
                button.setChecked(False)
            else:
                if int(button.text()) not in _annotations:
                    button.setChecked(False)

    def setCheckedAnnotations(self, _annotations):
        """
        check all buttons in accordance with annotations
        """
        for button in self.__button_group__.buttons():
            if not button == self.__all_button__:
                if int(button.text()) in _annotations:
                    button.setChecked(True)

    def isAllUnchecked(self):
        return self.__button_group__.isAllUnchecked()

    def __createAnnotationButtons__(self):

        self.__button_group__ = ButtonGroupWidget(self)

        unique_annotations0 = get_unique_annotations(
                                                self.data_accessor.annotation0)
        empty = is_empty(unique_annotations0)
        self.set_title(empty)
        self.__all_button__ = CheckBoxWidget(self, i18n_def='ALL',
                                clicked_handler=self.__all_button_handler__)
        self.__button_group__.addButton(self.__all_button__)
        for unique_annotation in unique_annotations0:
            annotationCheckBox = CheckBoxWidget(self,
                                            i18n_def=str(unique_annotation))
            self.__button_group__.addButton(annotationCheckBox)

        self.__button_group__.setExclusive(False)
        self.__button_group__.connect(self.__button_group__,
                                      BUTTON_CLICKED_SIGNAL,
                                      self.__button_handler__)

    def __button_handler__(self, button):
        if button.isChecked():
            if button == self.__all_button__:
                self.__setCheckedAnnotationsButtons__(False)
                self.__setEnabledAnnotationsButtons__(False)
            self.__activateActionButton__(True)
        else:
            if button == self.__all_button__ or \
                self.__button_group__.isAllUnchecked():
                self.__activateActionButton__(False)
            if button == self.__all_button__:
                self.__setEnabledAnnotationsButtons__(True)

    def __all_button_handler__(self):
        self.__button_handler__(self.__all_button__)

    def __setCheckedAnnotationsButtons__(self, _checked):
        for button in self.__button_group__.buttons():
            if not button == self.__all_button__:
                button.setChecked(_checked)

    def __setEnabledAnnotationsButtons__(self, _enabled):
        for button in self.__button_group__.buttons():
            if not button == self.__all_button__:
                button.setEnabled(_enabled)

    def __activateActionButton__(self, _activate):
        self.action_button.setEnabled(_activate)
        if _activate == False and hasattr(self.action_button, 'setChecked'):
            self.action_button.setChecked(False)

    def useFilter(self):
        return self.action_button.isChecked() \
            if hasattr(self.action_button, 'isChecked') else False

    def getFilter(self):
        return self.__filter__

    def setAnnotationFilterParams(self, annotation_filter_params):
        """
        set up annotation filter widget parameters
        """
        if not annotation_filter_params.all_annotations:
            if not annotation_filter_params.annotations == None:
                self.setEnabledAnnotations(annotation_filter_params.annotations) # @IgnorePep8
                self.setCheckedAnnotations(annotation_filter_params.annotations) # @IgnorePep8

        self.__all_button__.setChecked(
                                    annotation_filter_params.all_annotations)
        self.__all_button__.setEnabled(True)

        self.__action_button__.setChecked(annotation_filter_params.use_filter)
        if annotation_filter_params.use_filter or \
            annotation_filter_params.all_annotations or \
            not annotation_filter_params.annotations == None:
            self.__action_button__.setEnabled(True)

    def getAnnotationFilterParams(self):
        all_annotations = False
        annotations = self.excluded_annotations
        if annotations == ALL_ANNOTATIONS \
            or self.__all_button__.isChecked():
            all_annotations = True
            annotations = None
        if not annotations == None and len(annotations) == 0:
            annotations = None
        return AnnotationFilterParams(annotations, all_annotations,
                                      self.useFilter())
