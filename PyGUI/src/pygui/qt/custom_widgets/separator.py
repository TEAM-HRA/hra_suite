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
            signCheckBox = createCheckBox(self.separators)
            signCheckBox.setText(label)
            self.buttonGroup.addButton(signCheckBox)
            if label == SeparatorSign.CUSTOM.label:
                self.customSeparator = createLineEdit(self.separators,
                                             maxLength=15,
                                             width=get_width_of_n_letters(14),
                                             enabled=False)
        self.groupSeparator.connect(self.buttonGroup,
                     SIGNAL("buttonClicked(QAbstractButton *)"),
                     self.buttonClicked)
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
        if button.text() == SeparatorSign.CUSTOM.label:
            self.customSeparator.setEnabled(True)
            self.customSeparator.setFocus()
        else:
            self.customSeparator.setEnabled(False)

    def checkGlobalSettings(self):
        if self.globalSettings.checkState() == Qt.Checked:
            if self.buttonGroup.checkedButton() == None \
              or is_empty(self.customSeparator.text()):
                Information(information='A separator have to be chosen !')
                self.globalSettings.setCheckState(Qt.Unchecked)
            else:
                self.separators.setEnabled(False)
        else:
            self.separators.setEnabled(True)


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
