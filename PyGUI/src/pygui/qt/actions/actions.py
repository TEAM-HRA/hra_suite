'''
Created on 29-10-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycore.globals import GLOBALS
from pycore.properties import Properties
from pygui.qt.utils.graphics import get_resource_as_icon
from pycore.introspection import get_method_member_object


class SlotWrapper(object):
    def __init__(self, _slot, **_dargs):
        self.__slot__ = _slot
        self.__dargs__ = _dargs

    def __call__(self, *args):
        _class_method = get_method_member_object(self.__slot__)
        if _class_method:
            return _class_method(self.__dargs__)
        QMessageBox.information(None, "Information",
                            "Action '" + self.__slot__ + "' doesn't exist !!!")


def create_action(parent, action_spec):
    if not action_spec.title:
        return
    slot = None
    if not action_spec.slot == None:
        #action_spec.slot could be a method or a function
        slot = action_spec.slot if hasattr(action_spec.slot, '__call__') else \
                SlotWrapper(action_spec.slot, parent=parent)
    if action_spec.signal == None and action_spec.slot:
        qt_action = QAction(action_spec.title, parent, triggered=slot)
    else:
        qt_action = QAction(action_spec.title, parent)
    if action_spec.iconId:
        icon = _ICONS_PROPERTIES.getValue(action_spec.iconId)
        if icon:
            qt_action.setIcon(get_resource_as_icon(icon))
        #qt_action.setIcon(QIcon(":/%s.png" % icon))
    #if shortcut is not None:
    #    qt_action.setShortcut(shortcut)
    if action_spec.tipId:
        tooltip = _TOOLTIPS_PROPERTIES.getValue(action_spec.tipId)
        if tooltip:
            qt_action.setToolTip(tooltip)
            qt_action.setStatusTip(tooltip)
    if action_spec.signal and action_spec.slot:
        parent.connect(qt_action, SIGNAL(action_spec.signal), slot)
    qt_action.setCheckable(action_spec.checkable)
    return qt_action


_ICONS_PROPERTIES = Properties(GLOBALS.get(ICONS_FILE=GLOBALS.ITEM),
                               _file_prefix=GLOBALS.SETTINGS_DIR,
                               _use_as_resources=GLOBALS.USE_SETTINGS_EGG)
_TOOLTIPS_PROPERTIES = Properties(GLOBALS.get(TOOLTIPS_FILE=GLOBALS.ITEM))
