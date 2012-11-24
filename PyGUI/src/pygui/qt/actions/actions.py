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


class SlotWrapper(object):
    def __init__(self, _slot, **_dargs):
        self.__slot__ = _slot
        self.__dargs__ = _dargs

    def __call__(self, *args):
        _module = __import__(self.__package, fromlist=[self.__class])
        if _module:
            _class_object = getattr(_module, self.__class, None)
            if _class_object:
                _class_method = getattr(_class_object, self.__method, None)
                if _class_method:
                    return _class_method(self.__dargs__)

        QMessageBox.information(None, "Information",
                            "Action '" + self.__slot__ + "' doesn't exist !!!")

    @property
    def __method(self):
        return self.__part(-1)

    @property
    def __class(self):
        return self.__part(-2)

    @property
    def __module(self):
        return self.__part(-3)

    @property
    def __package(self):
        return self.__part(0, -2)

    def __part(self, start, end=None):
        splits = self.__slot__.split(".")
        return splits[start] if end == None else ".".join(splits[start:end])


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
            slot = SlotWrapper(action.slot, parent=self.__parent)
            self.__parent.connect(qt_action, SIGNAL(action.signal), slot)
        if action.type == Action.CHECKABLE:
            qt_action.setCheckable(True)
        return qt_action


_ICONS_PROPERTIES = Properties(GLOBALS.get(ICONS_FILE=GLOBALS.ITEM),
                               _file_prefix=GLOBALS.SETTINGS_DIR,
                               _use_as_resources=GLOBALS.USE_SETTINGS_EGG)
_TOOLTIPS_PROPERTIES = Properties(GLOBALS.get(TOOLTIPS_FILE=GLOBALS.ITEM))
