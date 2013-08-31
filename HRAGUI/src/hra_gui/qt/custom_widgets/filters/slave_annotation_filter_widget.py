'''
Created on 23-03-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    import pylab as pl
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    #from hra_core.collections_utils import is_empty
    from hra_core.misc import is_empty
    from hra_math.model.data_vector_listener import DataVectorListener
    from hra_math.model.utils import ALL_ANNOTATIONS
    from hra_gui.qt.widgets.check_box_widget import CheckBoxWidget
    from hra_gui.qt.custom_widgets.filters.common_annotation_filter_widget import CommonAnnotationFilterWidget # @IgnorePep8    
except ImportError as error:
    ImportErrorMessage(error, __name__)


class SlaveAnnotationFilterWidget(CommonAnnotationFilterWidget):
    def __init__(self, parent, **params):
        super(SlaveAnnotationFilterWidget, self).__init__(parent, **params)
        self.data_accessor.addListener(self,
                                __AnnotationFilterDataVectorListener__(self))
        self.setAnnotationsButtons(self.data_accessor.annotation)

    @property
    def action_button(self):
        return self.__action_button__

    def createActionButton(self):
        self.__action_button__ = CheckBoxWidget(self, i18n_def='Use filter')
        self.__action_button__.setChecked(False)
        self.__action_button__.setEnabled(False)

    def setAnnotationsButtons(self, _annotation):
        empty = is_empty(_annotation) or pl.sum(_annotation) == 0
        self.set_title(empty)
        if empty:
            self.reset()
        else:
            unique = list(pl.unique(_annotation))
            if len(unique) == self.buttons_count:
                self.setEnabledAnnotations(ALL_ANNOTATIONS)
            else:
                self.setEnabledAnnotations(unique)
                self.setUncheckNotAnnotations(unique)
            if self.isAllUnchecked():
                self.__action_button__.setChecked(False)
                self.__action_button__.setEnabled(False)


class __AnnotationFilterDataVectorListener__(DataVectorListener):
    """
    class change slave annotation widget if annotation data is changed
    """
    def __init__(self, _filter_widget):
        self.__filter_widget__ = _filter_widget

    def changeAnnotation(self, _annotation, **params):
        self.__filter_widget__.setAnnotationsButtons(_annotation)
