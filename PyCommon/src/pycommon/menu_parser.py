'''
Created on 20-10-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from xml.sax import make_parser
    from xml.sax import ContentHandler
    from xml.sax import SAXParseException
    from pycommon.actions import ActionSpec
except ImportError as error:
    ImportErrorMessage(error, __name__)


class MenuBuilder(object):

    def __init__(self):
        self.__handler__ = None

    def parse(self, filename_or_resource):
        try:
            self.__handler__ = _MenuBuilderHandler()
            parser = make_parser()
            parser.setContentHandler(self.__handler__)
            parser.parse(filename_or_resource)
            return True
        except (EnvironmentError, ValueError, SAXParseException) as err:
            print(err)
            return False

    def getMainMenus(self):
        return self.__handler__.getMainMenus()

    def getMenuItem(self, menu_ident, _menus=None):
        menus = self.getMainMenus() if _menus == None else _menus.subItems
        for menuItem in menus:
            if menuItem.isMenu():
                menuItem = self.getMenuItem(menu_ident, menuItem)
                if menuItem:
                    return menuItem
            else:
                if menu_ident == menuItem.ident:
                    return menuItem


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
        self.__actions_specs = []
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

        elif name == _MenuBuilderHandler.__ACTIONS_ID:
            self.__actions_specs = []

        elif name == _MenuBuilderHandler.__ACTION_ID:
            action_spec = ActionSpec()
            for key, value in attributes.items():
                action_spec.__setattr__(key, value)
            self.__actions_specs.append(action_spec)

    def endElement(self, name):
        if name == _MenuBuilderHandler.__MENU_ID:
            self.__parent_menus.pop()
            self.__level -= 1

        elif name == _MenuBuilderHandler.__MENU_ITEM_ID:
            if self.__menuItem:
                self.__menuItem.actions_specs = self.__actions_specs
            self.__actions_specs = []

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
        self.__actions_specs = []

    @property
    def actions_specs(self):
        return self.__actions_specs

    @actions_specs.setter
    def actions_specs(self, _actions_specs):
        self.__actions_specs = _actions_specs
