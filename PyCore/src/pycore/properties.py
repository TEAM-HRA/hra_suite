'''
Created on 29-10-2012

@author: jurek
'''
import configobj as cfg
from os.path import join


class Properties(object):

    def __init__(self, _file, _file_marker=None, _file_prefix=None):
        self.__properties = cfg.ConfigObj(_file)
        self.__file_marker = _file_marker
        self.__file_prefix = _file_prefix

    def getValue(self, _id):
        value = self.properties.get(_id, None)
        return join(self.__file_prefix, value[len(self.__file_marker):]) \
            if value and value.startswith(self.__file_marker) else value

    def getValueAsBool(self, _id):
        value = self.properties.get(_id)
        if value and value.lower() in ("false", "true"):
            value = bool("true" == value.lower())
        return value

    @property
    def properties(self):
        return self.__properties

    @property
    def items(self):
        return self.properties.items()
