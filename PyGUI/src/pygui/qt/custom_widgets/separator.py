'''
Created on 13-12-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.widgets import createGroupBox
from pygui.qt.utils.widgets import createComposite
from pygui.qt.utils.widgets import createCheckBox
from pygui.qt.utils.widgets import createButtonGroup
from pygui.qt.utils.widgets import createLineEdit
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.graphics import get_width_of_n_letters
from pygui.qt.utils.windows import InformationWindow
from pycore.misc import is_empty
from pycore.misc import Params


class DataSeparatorWidget(object):

    def __init__(self, parent, **params):
        self.params = Params(**params)
        self.separatorsGroupBox = createGroupBox(parent,
                                    i18n="separator.widget.group.title",
                                    i18n_def="Separator",
                                    layout=QVBoxLayout())

        self.predefinedSeparatorsComposite = createComposite(
                                                    self.separatorsGroupBox,
                                                    layout=QHBoxLayout())
        self.predefinedSeparatorsButtonsGroup = createButtonGroup(
                                            self.predefinedSeparatorsComposite)

        self.predefinedSeparatorsLabels = SeparatorSign.getSeparatorLabels()
        for (_, _, label) in self.predefinedSeparatorsLabels:
            if not label == SeparatorSign.CUSTOM.label:
                predefinedSeparatorCheckBox = createCheckBox(
                                            self.predefinedSeparatorsComposite)
                predefinedSeparatorCheckBox.setText(label)
                self.predefinedSeparatorsButtonsGroup.addButton(
                                                predefinedSeparatorCheckBox)

        self.separatorsGroupBox.connect(self.predefinedSeparatorsButtonsGroup,
                                    SIGNAL("buttonClicked(QAbstractButton *)"),
                                    self.predefinedSeparatorButtonClicked)

        self.customSeparatorEdit = createLineEdit(
                        self.predefinedSeparatorsComposite,
                        maxLength=15,
                        width=get_width_of_n_letters(14),
                        focusEventHandler=self.customSeparatorButtonClicked)
        self.separatorsGroupBox.connect(self.customSeparatorEdit,
                                        SIGNAL("textChanged(const QString&)"),
                                        self.customSeparatorEditChanged)

        self.customSeparatorCheckBox = createCheckBox(
                                        self.predefinedSeparatorsComposite,
                                        i18n="separator.custom.checkbox",
                                        i18n_def="Custom",
                                        enabled=False)
        self.separatorsGroupBox.connect(self.customSeparatorCheckBox,
                                        SIGNAL("clicked()"),
                                        self.customSeparatorButtonClicked)

        self.globalSettingsCheckBox = None
        if self.params.global_marker:
            self.globalSettingsCheckBox = createCheckBox(
                                                self.separatorsGroupBox,
                                                i18n="separator.global.marker",
                                                i18n_def="Global settings")
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
        self.customSeparatorCheckBox.setCheckState(Qt.Unchecked)
        self.customSeparatorCheckBox.setEnabled(False)
        self.customSeparatorEdit.setText("")
        if self.params.separatorHandler and \
            not self.predefinedSeparatorsButtonsGroup.checkedButton() == None:
            self.params.separatorHandler(self.__getPredefinedSeparatorSign__())

    def customSeparatorEditChanged(self, _text):
        self.customSeparatorButtonClicked()
        self.customSeparatorCheckBox.setEnabled(_text.size() > 0)

    def globalSettingsButtonClicked(self):
        if self.globalSettingsCheckBox.checkState() == Qt.Checked:
            if not self.predefinedSeparatorsButtonsGroup.checkedButton() \
                == None \
              or not is_empty(self.customSeparatorEdit.text()):
                self.predefinedSeparatorsComposite.setEnabled(False)
            else:
                self.globalSettingsCheckBox.setCheckState(Qt.Unchecked)
                InformationWindow(
                                information='A separator must be chosen !')
        else:
            self.predefinedSeparatorsComposite.setEnabled(True)

    def customSeparatorButtonClicked(self):
        #to uncheck button included in a button group one have to use a trick:
        #change to none exclusive state behaviour of the button group, then
        #uncheck checked button and reverse to previous exclusive state of
        #the button group
        if self.predefinedSeparatorsButtonsGroup.checkedButton():
            self.predefinedSeparatorsButtonsGroup.setExclusive(False)
            self.predefinedSeparatorsButtonsGroup.checkedButton().setChecked(
                                                                        False)
            self.predefinedSeparatorsButtonsGroup.setExclusive(True)

        if self.customSeparatorCheckBox.checkState() == Qt.Checked and \
            self.params.separatorHandler:
            self.params.separatorHandler(self.__getCustomSeparatorSign__())

    def __getPredefinedSeparatorSign__(self):
        button = self.predefinedSeparatorsButtonsGroup.checkedButton()
        if not button == None:
            for (_, sign, label) in self.predefinedSeparatorsLabels:
                if button.text() == label:
                    return sign

    def __getCustomSeparatorSign__(self):
        if self.customSeparatorCheckBox.checkState() == Qt.Checked:
            return self.customSeparatorEdit.text()

    def setEnabled(self, enabled):
        if not enabled == None:
            self.separatorsGroupBox.setEnabled(enabled)


class SeparatorSign(object):

    COUNTER = 0

    def __init__(self, sign, i18n, i18n_def):
        self.sign = sign
        self.i18n = i18n
        self.i18n_def = i18n_def
        SeparatorSign.COUNTER = SeparatorSign.COUNTER + 1
        self.counter = SeparatorSign.COUNTER

    @property
    def label(self):
        if hasattr(self.sign, '__len__') and len(self.sign.strip()) > 0:
            return "%s [ %s ]" % (QT_I18N(self.i18n, self.i18n_def), self.sign)
        else:
            return QT_I18N(self.i18n, self.i18n_def)

    @staticmethod
    def getSeparatorSign(sign):
        for member in dir(SeparatorSign):
            separator = getattr(SeparatorSign, member)
            if isinstance(separator, SeparatorSign) and separator.sign == sign:
                return separator
        return SeparatorSign.CUSTOM if not sign == None else SeparatorSign.NONE

    @staticmethod
    def getSeparatorLabels():
        labels = []
        for member in dir(SeparatorSign):
            separator = getattr(SeparatorSign, member)
            if isinstance(separator, SeparatorSign):
                if not separator == SeparatorSign.NONE:
                    labels.append((separator.counter, separator.sign,
                                   separator.label, ))
        return sorted(labels, key=lambda separator: separator[0])


SeparatorSign.NONE = SeparatorSign('', '', '')
SeparatorSign.SPACE = SeparatorSign(' ', 'separator.space', 'Space')
SeparatorSign.TAB = SeparatorSign('\t', 'separator.tab', 'Tab')
SeparatorSign.SEMICOLON = SeparatorSign(';', 'separator.semicolon',
                                        'Semicolon')
SeparatorSign.DASH = SeparatorSign('-', 'separator.dash', 'Dash')
SeparatorSign.COMMA = SeparatorSign(',', 'separator.comma', 'Comma')
SeparatorSign.CUSTOM = SeparatorSign(-1, 'separator.custom', 'Custom')
