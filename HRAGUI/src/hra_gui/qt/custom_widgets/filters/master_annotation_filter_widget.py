'''
Created on 23-03-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.custom_widgets.filters.common_annotation_filter_widget import CommonAnnotationFilterWidget # @IgnorePep8    
    from hra_gui.qt.custom_widgets.filters.filter_utils import run_filter
except ImportError as error:
    ImportErrorMessage(error, __name__)


class MasterAnnotationFilterWidget(CommonAnnotationFilterWidget):
    def __init__(self, parent, **params):
        super(MasterAnnotationFilterWidget, self).__init__(parent, **params)

    @property
    def action_button(self):
        return self.__action_button__

    def createActionButton(self):
        self.__action_button__ = PushButtonWidget(self, i18n_def='Apply',
                                clicked_handler=self.__annotation_handler__)
        self.__action_button__.setChecked(False)
        self.__action_button__.setEnabled(False)

    def __annotation_handler__(self):
        self.annotation_filter.excluded_annotations = self.excluded_annotations
        run_filter(self.parent(), self.annotation_filter, self.data_accessor,
                   filter_name='annotation')
        self.setDisabledAnnotations(self.excluded_annotations)
        self.disableIfAllChecked()
        self.__action_button__.setEnabled(False)
