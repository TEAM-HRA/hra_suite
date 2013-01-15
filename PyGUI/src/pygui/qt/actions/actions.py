'''
Created on 29-10-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycommon.menu_action import Action
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


class ActionBuilder(object):
    def __init__(self, parent):
        self.__parent = parent

    def createAction(self, action):
        if not action.title:
            return
        qt_action = QAction(action.title, self.__parent)
        if action.iconId:
            icon = _ICONS_PROPERTIES.getValue(action.iconId)
            if icon:
                qt_action.setIcon(get_resource_as_icon(icon))
            #qt_action.setIcon(QIcon(":/%s.png" % icon))
        #if shortcut is not None:
        #    qt_action.setShortcut(shortcut)
        if action.tipId:
            tooltip = _TOOLTIPS_PROPERTIES.getValue(action.tipId)
            if tooltip:
                qt_action.setToolTip(tooltip)
                qt_action.setStatusTip(tooltip)
        if action.signal and action.slot:
            slot = SlotWrapper(action.slot, parent=self.__parent)
            self.__parent.connect(qt_action, SIGNAL(action.signal), slot)
        if action.type == Action.CHECKABLE:
            qt_action.setCheckable(True)
        return qt_action


_ICONS_PROPERTIES = Properties(GLOBALS.get(ICONS_FILE=GLOBALS.ITEM),
                               _file_prefix=GLOBALS.SETTINGS_DIR,
                               _use_as_resources=GLOBALS.USE_SETTINGS_EGG)
_TOOLTIPS_PROPERTIES = Properties(GLOBALS.get(TOOLTIPS_FILE=GLOBALS.ITEM))
