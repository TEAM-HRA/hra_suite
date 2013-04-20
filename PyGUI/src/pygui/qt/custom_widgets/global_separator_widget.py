'''
Created on 13-12-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.misc import is_empty
    from pycore.misc import Params
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.windows import InformationWindow
    from pygui.qt.custom_widgets.separator_widget import SeparatorWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class GlobalSeparatorWidget(SeparatorWidget):

    def __init__(self, parent, **params):
        super(GlobalSeparatorWidget, self).__init__(parent, **params)
        self.params = Params(**params)

        self.globalSettingsCheckBox = None
        if self.params.globalHandler:
            self.globalSettingsCheckBox = CheckBoxCommon(
                                        self.separatorsGroupBox,
                                        i18n="separator.global.separator",
                                        i18n_def="Global separator")
            self.separatorsGroupBox.connect(self.globalSettingsCheckBox,
                                        SIGNAL("clicked()"),
                                        self.globalSettingsButtonClicked)

    def globalSettingsButtonClicked(self, clicked=None):
        if clicked:
            self.globalSettingsCheckBox.setChecked(clicked)
        if self.globalSettingsCheckBox.isChecked():
            if not self.predefinedSeparatorsButtonsGroup.checkedButton() \
                == None \
              or not is_empty(self.customSeparatorEdit.text()):
                self.predefinedSeparatorsComposite.setEnabled(False)
                self.params.globalHandler(True, self.getSeparatorSign())
            else:
                self.globalSettingsCheckBox.setChecked(False)
                InformationWindow(message='A separator must be chosen !')
        else:
            self.predefinedSeparatorsComposite.setEnabled(True)
            self.params.globalHandler(False)

    def setGlobalSeparatorAsDefault(self):
        self.globalSettingsButtonClicked(True)
