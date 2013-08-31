'''
Created on 17-11-2012

@author: jurek
'''
from pkgutil import get_data
from StringIO import StringIO
from hra_core.misc import is_empty


def get_application_settings(settings_package, settings_name):
    return get_resource_item(
        'settings.etc' if is_empty(settings_package) else settings_package,
        'settings.properties' if is_empty(settings_name) else settings_name)


def get_resource_item(package, resource_name):
    return ResourceItem(package, resource_name)


def is_resource(resource_item):
    return True if isinstance(resource_item, ResourceItem) else False


def get_as_resource_handler_or_string(resource_item):
    return resource_item.handler \
            if is_resource(resource_item) else str(resource_item)


def close_resource(resource_item):
    if is_resource(resource_item):
        resource_item.close()


class ResourceItem():
    """
    a class which represents a resource composed of two parts:
    _package - a package in dot notation
    _resource - a resource included in a package
    """
    def __init__(self, _package, _resource):
        self.__package__ = _package
        self.__resource__ = _resource
        self.__handler = None

    @property
    def package(self):
        return self.__package__

    @property
    def resource(self):
        return self.__resource__

    @resource.setter
    def resource(self, _resource):
        self.__resource__ = _resource

    def __str__(self):
        return "(" + self.package + ", " + self.resource + ")"

    @property
    def handler(self):
        data = get_data(self.package, self.resource)
        self.__handler = StringIO(data) if data else None
        return self.__handler

    @property
    def data(self):
        _handler = self.handler
        if _handler:
            _data = _handler.getvalue()
            _handler.close()
            return _data

    def close(self):
        if self.handler:
            self.handler.close()
