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
from pygui.qt.utils.windows import Information
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

        self.separatorLabels = SeparatorSign.getSeparatorLabels()
        for (_, _, label) in self.separatorLabels:
            if not label == SeparatorSign.CUSTOM.label:
                predefinedSeparatorCheckBox = createCheckBox(
                                            self.predefinedSeparatorsComposite)
                predefinedSeparatorCheckBox.setText(label)
                self.predefinedSeparatorsButtonsGroup.addButton(
                                                predefinedSeparatorCheckBox)

        self.separatorsGroupBox.connect(self.predefinedSeparatorsButtonsGroup,
                                    SIGNAL("buttonClicked(QAbstractButton *)"),
                                    self.buttonClicked)

        self.customSeparatorEdit = createLineEdit(
                                self.predefinedSeparatorsComposite,
                                maxLength=15,
                                width=get_width_of_n_letters(14),
                                focusEventHandler=self.customCheckBoxChanged)
        self.separatorsGroupBox.connect(self.customSeparatorEdit,
                                        SIGNAL("textChanged(const QString&)"),
                                        self.customSeparatorChanged)

        self.customSeparatorCheckBox = createCheckBox(
                                        self.predefinedSeparatorsComposite,
                                        i18n="separator.custom.checkbox",
                                        i18n_def="Custom",
                                        enabled=False)
        self.separatorsGroupBox.connect(self.customSeparatorCheckBox,
                                        SIGNAL("clicked()"),
                                        self.customCheckBoxChanged)

        self.globalSettings = None
        if self.params.global_marker:
            self.globalSettings = createCheckBox(self.separatorsGroupBox,
                                                i18n="separator.global.marker",
                                                i18n_def="Global settings")
            self.separatorsGroupBox.connect(self.globalSettings,
                                        SIGNAL("clicked()"),
                                        self.checkGlobalSettings)

    def getSeparatorSign(self):
        button = self.predefinedSeparatorsButtonsGroup.checkedButton()
        return self.customSeparatorEdit.text() \
                if button == SeparatorSign.CUSTOM else button.text()

    def buttonClicked(self, button):
        self.customSeparatorCheckBox.setCheckState(Qt.Unchecked)
        self.customSeparatorCheckBox.setEnabled(False)
        self.customSeparatorEdit.setText("")

    def customSeparatorChanged(self, _text):
        self.customCheckBoxChanged()
        self.customSeparatorCheckBox.setEnabled(_text.size() > 0)

    def checkGlobalSettings(self):
        if self.globalSettings.checkState() == Qt.Checked:
            if not self.predefinedSeparatorsButtonsGroup.checkedButton() \
                == None \
              or not is_empty(self.customSeparatorEdit.text()):
                self.predefinedSeparatorsComposite.setEnabled(False)
            else:
                Information(information='A separator have to be chosen !')
                self.globalSettings.setCheckState(Qt.Unchecked)
        else:
            self.predefinedSeparatorsComposite.setEnabled(True)

    def customCheckBoxChanged(self):
        #to uncheck button included in a button group one have to use a trick:
        #change to none exclusive state behaviour of the button group, then
        #uncheck checked button and reverse to previous exclusive state of
        #the button group
        if self.predefinedSeparatorsButtonsGroup.checkedButton():
            self.predefinedSeparatorsButtonsGroup.setExclusive(False)
            self.predefinedSeparatorsButtonsGroup.checkedButton().setChecked(
                                                                        False)
            self.predefinedSeparatorsButtonsGroup.setExclusive(True)


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
