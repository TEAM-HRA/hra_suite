'''
Created on 24-03-2013

@author: jurek
'''
from pymath.utils.utils import print_import_error
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.units import get_units_for_type
    from pycore.units import TimeUnit
    from pycore.units import Millisecond
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
    from pygui.qt.widgets.button_group_widget import ButtonGroupWidget
except ImportError as error:
    print_import_error(__name__, error)


class TimeUnitsWidget(GroupBoxWidget):

    def __init__(self, parent, **params):
        get_or_put(params, 'i18n', 'time.units.group.title')
        get_or_put(params, 'i18n_def', 'Time units')
        get_or_put(params, 'layout', QHBoxLayout())
        self.default_unit = params.get('default_unit', Millisecond)
        super(TimeUnitsWidget, self).__init__(parent, **params)
        self.__unitsButtonsGroup__ = ButtonGroupWidget(self)
        self.__change_unit_handler__ = params.get('change_unit_handler', None)

        for time_unit in get_units_for_type(TimeUnit):
            unitCheckBox = CheckBoxWidget(self,
                    i18n_def="%s [%s]" % (time_unit.name, time_unit.label))

            #add artificially property unit for later use in getUnit method
            unitCheckBox.unit = time_unit

            if time_unit == self.default_unit:
                unitCheckBox.setChecked(True)
            self.__unitsButtonsGroup__.addButton(unitCheckBox)

        self.connect(self.__unitsButtonsGroup__,
                    SIGNAL("buttonClicked(QAbstractButton *)"),
                    self.__buttonClicked__)
        self.__old_button_unit__ = None

    def getUnit(self):
        unitCheckBox = self.__unitsButtonsGroup__.checkedButton()
        if unitCheckBox:
            return unitCheckBox.unit

    def addUnit(self, unit):
        unitCheckBox = CheckBoxWidget(self,
                    i18n_def="%s [%s]" % (unit.name, unit.label))
        unitCheckBox.unit = unit
        if unit == self.default_unit:
            unitCheckBox.setChecked(True)
        self.__unitsButtonsGroup__.addButton(unitCheckBox)

    def __buttonClicked__(self, button):
        if not button.unit == self.__old_button_unit__:
            if not self.__change_unit_handler__ == None:
                self.__change_unit_handler__(button.unit)
        self.__old_button_unit__ = button.unit
