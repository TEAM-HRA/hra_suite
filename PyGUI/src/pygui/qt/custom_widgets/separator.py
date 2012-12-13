'''
Created on 13-12-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.widgets import createGroupBox
from pygui.qt.utils.widgets import createCheckBox
from pygui.qt.utils.widgets import createButtonGroup
from pygui.qt.utils.widgets import createLineEdit
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.graphics import get_width_of_n_letters


class SeparatorWidget(object):
    def __init__(self, parent, default_separator=None):
        self.groupSeparator = createGroupBox(parent,
                                    i18n="separator.widget.group.title",
                                    i18n_def="Separator",
                                    layout=QHBoxLayout())
        self.buttonGroup = createButtonGroup(self.groupSeparator)
        self.separatorLabels = SeparatorSign.getSeparatorLabels()
        for (_, _, label) in self.separatorLabels:
            signCheckBox = createCheckBox(self.groupSeparator)
            signCheckBox.setText(label)
            self.buttonGroup.addButton(signCheckBox)
            if label == SeparatorSign.CUSTOM.label:
                self.customSeparator = createLineEdit(self.groupSeparator,
                                             maxLength=15,
                                             width=get_width_of_n_letters(14),
                                             enabled=False)
        self.buttonGroup.connect(self.buttonGroup,
                     SIGNAL("buttonClicked(QAbstractButton *)"),
                     self.buttonClicked)

    def getSeparatorSign(self):
        return self.separator_sing

    def buttonClicked(self, button):
        if button.text() == SeparatorSign.CUSTOM.label:
            self.customSeparator.setEnabled(True)
            self.customSeparator.setFocus()
        else:
            self.customSeparator.setEnabled(False)


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
    def getSeparatorSign(self, sign):
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
