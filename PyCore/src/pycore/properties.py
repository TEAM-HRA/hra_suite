'''
Created on 29-10-2012

@author: jurek
'''
import configobj as cfg
from os.path import join


class Properties(object):

    def __init__(self, _file, _file_marker='@', _file_prefix=None,
                 _check_booleans=False):
        self.__properties = cfg.ConfigObj(_file)
        self.__file_marker = _file_marker
        self.__file_prefix = _file_prefix
        self.__check_booleans = _check_booleans

    def getValue(self, _id):
        value = self.properties.get(_id, None)
        if value:
            if self.__check_booleans and self.isBoolValue(_id):
                value = bool("true" == value.lower())
            elif self.__file_marker and value.startswith(self.__file_marker):
                size = len(self.__file_marker)
                # the dot sign after self.__file_marker means relative path
                if value[size] == '.':
                    value = join(self.__file_prefix, value[size + 1:])
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
