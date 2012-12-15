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


class DataSeparatorWidget(object):
    def __init__(self, parent, default_separator=None, global_marker=True):
        self.groupSeparator = createGroupBox(parent,
                                    i18n="separator.widget.group.title",
                                    i18n_def="Separator",
                                    layout=QVBoxLayout())

        self.separators = createComposite(self.groupSeparator,
                                          layout=QHBoxLayout())
        self.buttonGroup = createButtonGroup(self.separators)
        self.separatorLabels = SeparatorSign.getSeparatorLabels()
        for (_, _, label) in self.separatorLabels:
            if not label == SeparatorSign.CUSTOM.label:
                signCheckBox = createCheckBox(self.separators)
                signCheckBox.setText(label)
                self.buttonGroup.addButton(signCheckBox)
        self.groupSeparator.connect(self.buttonGroup,
                                 SIGNAL("buttonClicked(QAbstractButton *)"),
                                 self.buttonClicked)

        self.customSeparator = createLineEdit(self.separators,
                                maxLength=15,
                                width=get_width_of_n_letters(14),
                                focusEventHandler=self.customCheckBoxChanged)
        self.groupSeparator.connect(self.customSeparator,
                                 SIGNAL("textChanged(const QString&)"),
                                 self.customSeparatorChanged)

        self.customCheckBox = createCheckBox(self.separators,
                                i18n="separator.custom.checkbox",
                                i18n_def="Custom",
                                enabled=False)
        self.groupSeparator.connect(self.customCheckBox,
                                    SIGNAL("clicked()"),
                                    self.customCheckBoxChanged)

        self.globalSettings = None
        if global_marker:
            self.globalSettings = createCheckBox(self.groupSeparator,
                                                i18n="separator.global.marker",
                                                i18n_def="Global settings")
            self.groupSeparator.connect(self.globalSettings,
                                        SIGNAL("clicked()"),
                                        self.checkGlobalSettings)

    def getSeparatorSign(self):
        button = self.buttonGroup.checkedButton()
        return self.customSeparator.text() if button == SeparatorSign.CUSTOM \
                                            else button.text()

    def buttonClicked(self, button):
        self.customCheckBox.setCheckState(Qt.Unchecked)
        self.customCheckBox.setEnabled(False)
        self.customSeparator.setText("")

    def customSeparatorChanged(self, _text):
        self.customCheckBoxChanged()
        self.customCheckBox.setEnabled(_text.size() > 0)

    def checkGlobalSettings(self):
        if self.globalSettings.checkState() == Qt.Checked:
            if not self.buttonGroup.checkedButton() == None \
              or not is_empty(self.customSeparator.text()):
                self.separators.setEnabled(False)
            else:
                Information(information='A separator have to be chosen !')
                self.globalSettings.setCheckState(Qt.Unchecked)
        else:
            self.separators.setEnabled(True)

    def customCheckBoxChanged(self):
        #to uncheck button included in a button group one have to use a trick:
        #change to none exclusive state behaviour of the button group, then
        #uncheck checked button and reverse to previous exclusive state of
        #the button group
        if self.buttonGroup.checkedButton():
            self.buttonGroup.setExclusive(False)
            self.buttonGroup.checkedButton().setChecked(False)
            self.buttonGroup.setExclusive(True)


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
SeparatorSign.CUSTOM = SeparatorSign(-1, 'separator.customCheckBox', 'Custom')
