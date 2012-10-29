'''
Created on 20-10-2012

@author: jurek
'''

from xml.sax import make_parser
from xml.sax import ContentHandler
from xml.sax import SAXParseException


class MenuBuilder(object):

    def __init__(self):
        self.__handler__ = None

    def parse(self, filename):
        try:
            self.__handler__ = _MenuBuilderHandler()
            parser = make_parser()
            parser.setContentHandler(self.__handler__)
            parser.parse(filename)
            return True
        except (EnvironmentError, ValueError, SAXParseException) as err:
            print(err)
            return False

    def getMainMenus(self):
        return self.__handler__.getMainMenus()


class _MenuBuilderHandler(ContentHandler):

    __MENU_ID = "menu"
    __MENU_ITEM_ID = "menuItem"
    __ACTIONS_ID = "actions"
    __ACTION_ID = "action"

    def __init__(self):
        ContentHandler.__init__(self)
        self.__level = -1
        self.__main_menus = []
        self.__parent_menus = []
        self.__actions = []
        self.__menuItem = None

    def startElement(self, name, attributes):
        if name == _MenuBuilderHandler.__MENU_ID:
            menu = Menu()
            self.__parent_menus.append(menu)
            self.__level += 1
            if self.__level == 0:
                self.__main_menus.append(menu)  # add a top menu
            else:
                self.__parent_menus[self.__level - 1].addSubItem(menu)
            for key, value in attributes.items():
                menu.__setattr__(key, value)

        elif name == _MenuBuilderHandler.__MENU_ITEM_ID:
            self.__menuItem = MenuItem()
            for key, value in attributes.items():
                self.__menuItem.__setattr__(key, value)
            self.__parent_menus[self.__level].addSubItem(self.__menuItem)

        elif name == _MenuBuilderHandler.__ACTION_ID:
            action = Action()
            for key, value in attributes.items():
                action.__setattr__(key, value)

    def endElement(self, name):
        if name == _MenuBuilderHandler.__MENU_ID:
            self.__parent_menus.pop()
            self.__level -= 1

        elif name == _MenuBuilderHandler.__MENU_ITEM_ID:
            if self.__menuItem:
                self.__menuItem.actions = self.__actions
            self.__actions = []
            self.__menuItem = None

    def getMainMenus(self):
        return self.__main_menus


class _Item(object):
    def __init__(self, is_menu_item):
        self.__ident = None
        self.__title = None
        self.__is_menu = is_menu_item
        self.__sub_items = []  # includes sub menus and menu items

    @property
    def ident(self):
        return self.__ident

    @ident.setter
    def ident(self, ident):
        self.__ident = ident

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        self.__title = title

    def isMenu(self):
        return self.__is_menu

    def addSubItem(self, sub_item):
        self.__sub_items.append(sub_item)

    @property
    def subItems(self):
        return self.__sub_items


class Menu(_Item):
    def __init__(self):
        _Item.__init__(self, True)


class MenuItem(_Item):
    def __init__(self):
        _Item.__init__(self, False)
        self.__actions = []

    @property
    def actions(self):
        return self.__actions

    @actions.setter
    def actions(self, _actions):
        self.__actions = _actions


class Action(object):
    def __init__(self):
        self.__icondId = None
        self.__tipId = None
        self.__type = None
        self.__signal = None
        self.__slot = None

    @property
    def iconId(self):
        return self.__icondId

    @iconId.setter
    def iconId(self, _iconId):
        self.__icondId = _iconId

    @property
    def tipId(self):
        return self.__tipId

    @tipId.setter
    def tipId(self, _tipId):
        self.__tipId = _tipId

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, _type):
        self.__type = _type

    @property
    def signal(self):
        return self.__signal

    @signal.setter
    def signal(self, _signal):
        self.__signal = _signal

    @property
    def slot(self):
        return self.__stot

    @slot.setter
    def slot(self, _slot):
        self.__slot = _slot

if __name__ == '__main__':
    mb = MenuBuilder()
    if mb.parse("H:\\workspaces\\all\\doctorate\\PyCommon\\etc\\menus.xml"):
        menus = mb.getMainMenus()
        for menu in menus:
            print('ident: ' + menu.ident + ' title: ' + menu.title)
            for submenu in menu.subItems:
                print('   ident: ' + submenu.ident + ' title: ' + submenu.title) #@IgnorePep8
                for submenu2 in submenu.subItems:
                    print('       ident: ' + submenu2.ident + ' title: ' + submenu2.title) #@IgnorePep8
                    for submenu3 in submenu2.subItems:
                        print('           ident: ' + submenu3.ident + ' title: ' + submenu3.title) #@IgnorePep8
