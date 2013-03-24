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
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.widgets import ButtonGroupCommon
except ImportError as error:
    print_import_error(__name__, error)


class TimeUnitsWidget(GroupBoxCommon):

    def __init__(self, parent, **params):
        get_or_put(params, 'i18n', 'time.units.group.title')
        get_or_put(params, 'i18n_def', 'Time units')
        get_or_put(params, 'layout', QHBoxLayout())
        default_unit = params.get('default_unit', Millisecond)
        super(TimeUnitsWidget, self).__init__(parent, **params)
        self.unitsButtonsGroup = ButtonGroupCommon(self)

        for time_unit in get_units_for_type(TimeUnit):
            unitCheckBox = CheckBoxCommon(self,
                    i18n_def="%s [%s]" % (time_unit.name, time_unit.label))

            #add artificially property unit for later use in getUnit method
            unitCheckBox.unit = time_unit

            if time_unit == default_unit:
                unitCheckBox.setChecked(True)
            self.unitsButtonsGroup.addButton(unitCheckBox)

    def getUnit(self):
        unitCheckBox = self.unitsButtonsGroup.checkedButton()
        if unitCheckBox:
            return unitCheckBox.unit
