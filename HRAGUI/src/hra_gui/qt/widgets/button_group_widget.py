'''
Created on 21 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_gui.qt.widgets.commons import Common
    from hra_gui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ButtonGroupWidget(QButtonGroup, Common):
    def __init__(self, parent, **params):
        super(ButtonGroupWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)

    def isAllUnchecked(self):
        """
        return True when all buttons in button's group are unchecked
        """
        for button in self.buttons():
            if button.isChecked():
                return False
        return True

    def isAllChecked(self):
        """
        returns True when all buttons in button's group are checked
        """
        for button in self.buttons():
            if not button.isChecked():
                return False
        return True

    def setAllChecked(self, _checked):
        """
        check/uncheck all butoons in button's group
        """
        exclusive = self.exclusive()
        self.setExclusive(False)
        for button in self.buttons():
            button.setChecked(_checked)
        if exclusive:
            self.setExclusive(True)

    def setEnabled(self, _enabled):
        for button in self.buttons():
            button.setEnabled(_enabled)

    def isAnyChecked(self):
        """
        returns True when any button is checked
        """
        for button in self.buttons():
            if button.isChecked():
                return True
        return False
