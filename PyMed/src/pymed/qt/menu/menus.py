'''
Created on 28-10-2012

@author: jurek
'''
from pycommon.menu_utils import MenuBuilder
from pycore.globals import GLOBALS
from pymed.qt.actions.actions import QTActionBuilder


class QTMenuBuilder(object):
    def __init__(self, _parent):
        self.__parent = _parent
        self.__action_builder = QTActionBuilder(self.__parent)

    def createMenus(self):
        builder = MenuBuilder()
        builder.parse(GLOBALS.MENUS_FILE)
        menus = builder.getMainMenus()
        for menu in menus:
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
            _menu.addAction(self.__action_builder.createAction(action))