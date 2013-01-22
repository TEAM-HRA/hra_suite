'''
Created on 22-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.widgets import LabelCommon
    from pygui.qt.utils.widgets import LineEditCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ActivityWidget(CompositeCommon):
    """
    a widget used to input optional description text of activity
    """
    def __init__(self, parent, **params):
        super(ActivityWidget, self).__init__(parent, layout=QHBoxLayout(),
                                             **params)
        self.activityButton = CheckBoxCommon(self,
                            i18n="activity.button",
                            i18n_def="Save as activity",
                            clicked_handler=self.__clickedHandler__)

        LabelCommon(self,
                     i18n="activity.description.label",
                     i18n_def="Activity description (optional):")

        self.activityDescription = LineEditCommon(self, enabled=False)

    def activityOk(self):
        return self.activityButton.isChecked()

    def activityDescription(self):
        if self.activityButton.isChecked():
            return str(self.activityDescription.text())

    def __clickedHandler__(self):
        self.activityDescription.setEnabled(self.activityButton.isChecked())
