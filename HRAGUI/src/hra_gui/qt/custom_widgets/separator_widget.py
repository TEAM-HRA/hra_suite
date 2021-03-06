'''
Created on 13-12-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_core.collections_utils import get_or_put
    from hra_core.collections_utils import nvl
    from hra_core.misc import Params
    from hra_core.misc import Separator
    from hra_gui.qt.utils.qt_i18n import QT_I18N
    from hra_gui.qt.utils.graphics import get_width_of_n_letters
    from hra_gui.qt.widgets.group_box_widget import GroupBoxWidget
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.button_group_widget import ButtonGroupWidget
    from hra_gui.qt.widgets.check_box_widget import CheckBoxWidget
    from hra_gui.qt.widgets.line_edit_widget import LineEditWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


def separator_label_handler(separator):
    i18n = separator.id_
    i18n_def = separator.label
    if hasattr(separator.sign, '__len__') and len(separator.sign.strip()) > 0:
        return "%s [ %s ]" % (QT_I18N(i18n, i18n_def), separator.sign)
    else:
        return QT_I18N(i18n, i18n_def)


class SeparatorWidget(object):
    """
    widget used to choose a separator sign
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'i18n_def', 'Separator')
        self.params = Params(**params)
        self.separatorsGroupBox = GroupBoxWidget(parent,
                            i18n="separator.widget.group.title",
                            i18n_def=nvl(self.params.i18n_def, "Separator"),
                            layout=QVBoxLayout())

        self.predefinedSeparatorsComposite = CompositeWidget(
                                                    self.separatorsGroupBox,
                                                    layout=QHBoxLayout())
        self.predefinedSeparatorsButtonsGroup = ButtonGroupWidget(
                                            self.predefinedSeparatorsComposite)

        self.predefinedSeparatorsSpecs = Separator.getSeparatorsSpec(
                                                    separator_label_handler)
        for separatorSpec in self.predefinedSeparatorsSpecs:
            label = separatorSpec.label
            if not label == Separator.CUSTOM.label:  # @UndefinedVariable
                predefinedSeparatorCheckBox = CheckBoxWidget(
                                            self.predefinedSeparatorsComposite)
                #attach artificially a separatorSpec object used later in
                #def setSeparator(self, _separator) method
                predefinedSeparatorCheckBox.separator_spec = separatorSpec
                predefinedSeparatorCheckBox.setText(label)
                predefinedSeparatorCheckBox.sep_spec = separatorSpec
                if self.params.default_separator and \
                    separatorSpec.id_ == self.params.default_separator.id_:
                    predefinedSeparatorCheckBox.setChecked(True)
                self.predefinedSeparatorsButtonsGroup.addButton(
                                                predefinedSeparatorCheckBox)

        self.separatorsGroupBox.connect(self.predefinedSeparatorsButtonsGroup,
                                    SIGNAL("buttonClicked(QAbstractButton *)"),
                                    self.predefinedSeparatorButtonClicked)

        if not self.params.no_custom_separator == True:
            self.customSeparatorCheckBox = CheckBoxWidget(
                                        self.predefinedSeparatorsComposite,
                                        i18n="separator.custom.checkbox",
                                        i18n_def="Custom")
            self.customSeparatorCheckBox.sep_spec = Separator.CUSTOM
            self.separatorsGroupBox.connect(self.customSeparatorCheckBox,
                                        SIGNAL("clicked()"),
                                        self.customSeparatorButtonClicked)

            self.customSeparatorEdit = LineEditWidget(
                        self.predefinedSeparatorsComposite,
                        maxLength=15,
                        width=get_width_of_n_letters(14),
                        text_changed_handler=self.customSeparatorButtonClicked,
                        enabled=False)

        self.setEnabled(self.params.enabled)

    def getSeparatorSign(self):
        sign = self.__getPredefinedSeparatorSign__()
        if sign:
            return sign
        if not self.params.no_custom_separator == True:
            return self.__getCustomSeparatorSign__()

    def predefinedSeparatorButtonClicked(self, button):
        if not self.params.no_custom_separator == True:
            self.__customSeparatorClear__()
        if self.params.separatorHandler and \
            not self.predefinedSeparatorsButtonsGroup.checkedButton() == None:
            self.params.separatorHandler(self.__getPredefinedSeparatorSign__())

    def customSeparatorButtonClicked(self):
        checked = self.customSeparatorCheckBox.isChecked()
        separator = self.__getCustomSeparatorSign__()
        if checked and self.params.separatorHandler and separator:
            self.params.separatorHandler(separator)
        self.customSeparatorEdit.setEnabled(checked)
        if checked:
            self.__uncheckPredefinedButtons__()
            self.customSeparatorEdit.setFocus()

    def __getPredefinedSeparatorSign__(self):
        button = self.predefinedSeparatorsButtonsGroup.checkedButton()
        if not button == None:
            for (sign, _, label) in self.predefinedSeparatorsSpecs:
                if button.text() == label:
                    return sign

    def __getCustomSeparatorSign__(self):
        if self.customSeparatorCheckBox.isChecked():
            return str(self.customSeparatorEdit.text())

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
                    if button.sep_spec.id_ == separatorSign.id_:
                        if not self.params.no_custom_separator == True:
                            self.__customSeparatorClear__()
                        button.setChecked(True)
                        return

    def __customSeparatorClear__(self):
        self.customSeparatorCheckBox.setChecked(False)
        self.customSeparatorEdit.setText("")
        self.customSeparatorEdit.setEnabled(False)

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
