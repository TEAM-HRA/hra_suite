'''
Created on 29-10-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycommon.menu_utils import Action
from pycore.globals import GLOBALS
from pycore.properties import Properties
from pymed.qt.utils.context import Context
from pymed.qt.utils.graphics import get_resource_as_icon


class QTActionBuilder(object):
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
            _slot = action.slot_action
            Context(_slot).save(parent=self.__parent)
            self.__parent.connect(qt_action, SIGNAL(action.signal), _slot)
        if action.type == Action.CHECKABLE:
            qt_action.setCheckable(True)
        return qt_action


_ICONS_PROPERTIES = Properties(GLOBALS.get(ICONS_FILE=GLOBALS.ITEM),
                               _file_prefix=GLOBALS.SETTINGS_DIR,
                               _use_as_resources=GLOBALS.USE_SETTINGS_EGG)
_TOOLTIPS_PROPERTIES = Properties(GLOBALS.get(TOOLTIPS_FILE=GLOBALS.ITEM))
