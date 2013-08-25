'''
Created on 29-10-2012

@author: jurek
'''
import configobj as cfg
from os.path import join
from hra_core.resources import is_resource
from hra_core.resources import get_resource_item


class Properties(object):

    def __init__(self, _filename_or_resource, _file_marker='@',
                 _file_prefix=None, _check_booleans=False,
                 _use_as_resources=False):
        if is_resource(_filename_or_resource):
            self.__properties = cfg.ConfigObj(_filename_or_resource.handler)
            _filename_or_resource.close()
        else:
            self.__properties = cfg.ConfigObj(_filename_or_resource)
        self.__file_marker = _file_marker
        self.__file_prefix = _file_prefix
        self.__check_booleans = _check_booleans
        self.__use_as_resources = _use_as_resources

    def getValue(self, _id):
        value = self.properties.get(_id, None)
        if value:
            if self.__check_booleans and self.isBoolValue(_id):
                value = bool("true" == value.lower())
            elif self.__file_marker and value.startswith(self.__file_marker):
                size = len(self.__file_marker)
                # the dot sign after self.__file_marker means relative path
                if value[size] == '.':
                    value = join(self.__file_prefix, value[size + 1:]) \
                                if self.__file_prefix else value[size + 1:]
                    if self.__use_as_resources:
                        value = self.__get_as_resource_item(value)
                else:
                    value = value[size:]
        return value

    def isBoolValue(self, _id):
        value = self.properties.get(_id, None)
        return True if value and value.lower() in ("false", "true") else False

    @property
    def properties(self):
        return self.__properties

    @property
    def items(self):
        return [(key, self.getValue(key)) for key in self.properties.keys()]

    def __get_as_resource_item(self, value):
        if value:
            parts = value.split('\\\\')
            if len(parts) > 1:
                package = ".".join(parts[:-1])  # part up to the last
                resource = parts[len(parts) - 1:][0]  # the last part
                return get_resource_item(package, resource)
