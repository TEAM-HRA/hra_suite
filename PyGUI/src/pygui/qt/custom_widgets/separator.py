'''
Created on 13-12-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.widgets import ButtonGroupCommon
    from pygui.qt.utils.widgets import LineEditCommon
    from pygui.qt.utils.qt_i18n import QT_I18N
    from pygui.qt.utils.graphics import get_width_of_n_letters
    from pygui.qt.utils.windows import InformationWindow
    from pycore.misc import is_empty
    from pycore.misc import Params
    from pycore.misc import Separator
except ImportError as error:
    ImportErrorMessage(error, __name__)


def separator_label_handler(separator):
    i18n = separator.id_
    i18n_def = separator.label
    if hasattr(separator.sign, '__len__') and len(separator.sign.strip()) > 0:
        return "%s [ %s ]" % (QT_I18N(i18n, i18n_def), separator.sign)
    else:
        return QT_I18N(i18n, i18n_def)


class DataSeparatorWidget(object):

    def __init__(self, parent, **params):
        self.params = Params(**params)
        self.separatorsGroupBox = GroupBoxCommon(parent,
                                    i18n="separator.widget.group.title",
                                    i18n_def="Separator",
                                    layout=QVBoxLayout())

        self.predefinedSeparatorsComposite = CompositeCommon(
                                                    self.separatorsGroupBox,
                                                    layout=QHBoxLayout())
        self.predefinedSeparatorsButtonsGroup = ButtonGroupCommon(
                                            self.predefinedSeparatorsComposite)

        self.predefinedSeparatorsSpecs = Separator.getSeparatorsSpec(
                                                    separator_label_handler)
        for separatorSpec in self.predefinedSeparatorsSpecs:
            label = separatorSpec.label
            if not label == Separator.CUSTOM.label:  # @UndefinedVariable
                predefinedSeparatorCheckBox = CheckBoxCommon(
                                            self.predefinedSeparatorsComposite)
                #attach artificially a separatorSpec object used later in
                #def setSeparator(self, _separator) method
                predefinedSeparatorCheckBox.separator_spec = separatorSpec
                predefinedSeparatorCheckBox.setText(label)
                self.predefinedSeparatorsButtonsGroup.addButton(
                                                predefinedSeparatorCheckBox)

        self.separatorsGroupBox.connect(self.predefinedSeparatorsButtonsGroup,
                                    SIGNAL("buttonClicked(QAbstractButton *)"),
                                    self.predefinedSeparatorButtonClicked)

        self.customSeparatorEdit = LineEditCommon(
                        self.predefinedSeparatorsComposite,
                        maxLength=15,
                        width=get_width_of_n_letters(14),
                        focusEventHandler=self.customSeparatorButtonClicked)
        self.separatorsGroupBox.connect(self.customSeparatorEdit,
                                        SIGNAL("textChanged(const QString&)"),
                                        self.customSeparatorEditChanged)

        self.customSeparatorCheckBox = CheckBoxCommon(
                                        self.predefinedSeparatorsComposite,
                                        i18n="separator.custom.checkbox",
                                        i18n_def="Custom",
                                        enabled=False)
        self.separatorsGroupBox.connect(self.customSeparatorCheckBox,
                                        SIGNAL("clicked()"),
                                        self.customSeparatorButtonClicked)

        self.globalSettingsCheckBox = None
        if self.params.globalHandler:
            self.globalSettingsCheckBox = CheckBoxCommon(
                                        self.separatorsGroupBox,
                                        i18n="separator.global.separator",
                                        i18n_def="Global separator")
            self.separatorsGroupBox.connect(self.globalSettingsCheckBox,
                                        SIGNAL("clicked()"),
                                        self.globalSettingsButtonClicked)

        self.setEnabled(self.params.enabled)

    def getSeparatorSign(self):
        sign = self.__getPredefinedSeparatorSign__()
        if sign:
            return sign
        return self.__getCustomSeparatorSign__()

    def predefinedSeparatorButtonClicked(self, button):
        self.__customSeparatorClear__()
        if self.params.separatorHandler and \
            not self.predefinedSeparatorsButtonsGroup.checkedButton() == None:
            self.params.separatorHandler(self.__getPredefinedSeparatorSign__())

    def customSeparatorEditChanged(self, _text):
        self.customSeparatorButtonClicked()
        self.customSeparatorCheckBox.setEnabled(_text.size() > 0)

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

    def customSeparatorButtonClicked(self):
        self.__uncheckPredefinedButtons__()
        separator = self.__getCustomSeparatorSign__()
        if self.customSeparatorCheckBox.isChecked() and \
            self.params.separatorHandler and separator:
            self.params.separatorHandler(separator)

    def __getPredefinedSeparatorSign__(self):
        button = self.predefinedSeparatorsButtonsGroup.checkedButton()
        if not button == None:
            for (sign, _, label) in self.predefinedSeparatorsSpecs:
                if button.text() == label:
                    return sign

    def __getCustomSeparatorSign__(self):
        if self.customSeparatorCheckBox.isChecked():
            return self.customSeparatorEdit.text()

    def setEnabled(self, enabled):
        if not enabled == None:
            self.separatorsGroupBox.setEnabled(enabled)

    def setSeparator(self, _separator):
        if _separator:
            separatorSign = Separator.getSeparatorSign(_separator)
            if separatorSign == Separator.WHITE_SPACE:
                for button in self.predefinedSeparatorsButtonsGroup.buttons():
                    if button.separator_spec.id_ == Separator.WHITE_SPACE.id_:  # @UndefinedVariable @IgnorePep8
                        button.setChecked(True)
                        return
            elif separatorSign == Separator.CUSTOM:
                self.customSeparatorEdit.setText(_separator)
                self.__uncheckPredefinedButtons__()
            elif not separatorSign == Separator.NONE:
                for button in self.predefinedSeparatorsButtonsGroup.buttons():
                    if button.text() == separatorSign.label:
                        self.__customSeparatorClear__()
                        button.setChecked(True)
                        return

    def __customSeparatorClear__(self):
        self.customSeparatorCheckBox.setChecked(False)
        self.customSeparatorCheckBox.setEnabled(False)
        self.customSeparatorEdit.setText("")

    def __uncheckPredefinedButtons__(self):
        #to uncheck button included in a button group one have to use a trick:
        #change to none exclusive state behaviour of the button group, then
        #uncheck checked button and reverse to previous exclusive state of
        #the button group
        if self.predefinedSeparatorsButtonsGroup.checkedButton():
            self.predefinedSeparatorsButtonsGroup.setExclusive(False)
            self.predefinedSeparatorsButtonsGroup.checkedButton().setChecked(
                                                                        False)
            self.predefinedSeparatorsButtonsGroup.setExclusive(True)

    def setGlobalSeparatorAsDefault(self):
        self.globalSettingsButtonClicked(True)
