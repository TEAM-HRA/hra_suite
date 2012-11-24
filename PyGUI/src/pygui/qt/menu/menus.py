'''
Created on 28-10-2012

@author: jurek
'''
from pycommon.menu_parser import MenuBuilder
from pycore.globals import GLOBALS
from pygui.qt.actions.actions import QTActionBuilder
from pycore.resources import get_as_resource_handler_or_string
from pycore.resources import close_resource


class QTMenuBuilder(object):
    def __init__(self, _parent):
        self.__parent = _parent
        self.__action_builder = QTActionBuilder(self.__parent)

    def createMenus(self):
        builder = MenuBuilder()
        menus_resource = get_as_resource_handler_or_string(GLOBALS.MENUS_FILE)
        builder.parse(menus_resource)
        menus = builder.getMainMenus()
        for menu in menus:
            self.__createMenu(self.__parent.menuBar(), menu)
        close_resource(menus_resource)

    def __createMenu(self, _parent, menu):
        parent = _parent.addMenu(menu.title)
        for subItem in menu.subItems:
            if subItem.isMenu():
                self.__createMenu(parent, subItem)
            else:
                self.__createMenuItem(parent, subItem)

    def __createMenuItem(self, _menu, _menuItem):
        for action in _menuItem.actions:
            _menu.addAction(self.__action_builder.createAction(action))
