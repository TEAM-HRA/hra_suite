'''
Created on 28-10-2012

@author: jurek
'''
from pycommon.menu_parser import MenuBuilder
from pycore.globals import GLOBALS
from pygui.qt.actions.actions import create_action
from pygui.qt.actions.actions import SlotWrapper
from pycore.resources import get_as_resource_handler_or_string
from pycore.resources import close_resource


class QTMenuBuilder(object):
    def __init__(self, _parent):
        self.__parent = _parent
        self.__builder = None
        self.__main_menus = None

    def createMenus(self):
        for menu in self.__createMainMenus():
            self.__createMenu(self.__parent.menuBar(), menu)

    def __createMenu(self, _parent, menu):
        parent = _parent.addMenu(menu.title)
        for subItem in menu.subItems:
            if subItem.isMenu():
                self.__createMenu(parent, subItem)
            else:
                self.__createMenuItem(parent, subItem)

    def __createMenuItem(self, _menu, _menuItem):
        for action in _menuItem.actions:
            _menu.addAction(create_action(self.__parent, action))

    def __createMainMenus(self):
        if not self.__main_menus:
            self.__builder = MenuBuilder()
            menus_resource = get_as_resource_handler_or_string(GLOBALS.MENUS_FILE) #@IgnorePep8
            self.__builder.parse(menus_resource)
            self.__main_menus = self.__builder.getMainMenus()
            close_resource(menus_resource)
        return self.__main_menus

    def invokeMenuItem(self, menu_ident):
        self.__createMainMenus()
        menuItem = self.__builder.getMenuItem(menu_ident)
        if menuItem:
            for action in menuItem.actions:
                _slot = SlotWrapper(action.slot)
                if _slot:
                    _slot()
                    return True
        return False
