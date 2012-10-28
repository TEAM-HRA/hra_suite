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
            self.__handler__ = __MenuBuilderHandler()
            parser = make_parser()
            parser.setContentHandler(self.__handler__)
            parser.parse(filename)
            return True
        except (EnvironmentError, ValueError, SAXParseException) as err:
            print(err)
            return False

    def getMainMenus(self):
        return self.__handler__.getMainMenus()


class __MenuBuilderHandler(ContentHandler):

    __MENU_ID__ = "menu"
    __MENU_ITEM_ID__ = "menuItem"

    def __init__(self):
        ContentHandler.__init__(self)
        self.__level = -1
        self.__main_menus = []
        self.__parent_menus = []

    def startElement(self, name, attributes):
        if name == __MenuBuilderHandler.__MENU_ID__:
            menu = Menu()
            self.__parent_menus.append(menu)
            self.__level += 1
            if self.__level == 0:
                self.__main_menus.append(menu)  # add a top menu
            else:
                self.__parent_menus[self.__level - 1].addSubItem(menu)
            for key, value in attributes.items():
                menu.__setattr__(key, value)

        elif name == __MenuBuilderHandler.__MENU_ITEM_ID__:
            menuItem = MenuItem()
            for key, value in attributes.items():
                menuItem.__setattr__(key, value)
            self.__parent_menus[self.__level].addSubItem(menuItem)

    def endElement(self, name):
        if name == __MenuBuilderHandler.__MENU_ID__:
            self.__parent_menus.pop()
            self.__level -= 1

    def getMainMenus(self):
        return self.__main_menus


class __Item(object):
    def __init__(self, is_menu_item):
        self.__ident = None
        self.__title = None
        self.__is_menu_item = is_menu_item
        self.__sub_items = []  # includes sub menus and menu items
        self.__action = None
        self.__action_before = None
        self.__action_after = None

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

    def isMenuItem(self):
        return self.__is_menu_item

    def addSubItem(self, sub_item):
        self.__sub_items.append(sub_item)

    @property
    def subItems(self):
        return self.__sub_items

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, action):
        self.__action = action

    @property
    def actionBefore(self):
        return self.__action_before

    @actionBefore.setter
    def actionBefore(self, actionBefore):
        self.__action_before = actionBefore

    @property
    def actionAfter(self):
        return self.__action_after

    @actionAfter.setter
    def actionAfter(self, actionAfter):
        self.__action_after = actionAfter


class Menu(__Item):
    def __init__(self):
        __Item.__init__(self, False)


class MenuItem(__Item):
    def __init__(self):
        __Item.__init__(self, True)

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
