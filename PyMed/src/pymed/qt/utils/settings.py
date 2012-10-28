'''
Created on 23-10-2012

@author: jurek
'''

from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QVariant
from pycore.collections import get_other_keys


class SettingsFactory(object):
    @staticmethod
    def loadSettings(_target, *_setters, **params):
        (_settings, _prefix) = SettingsFactory._getInitials(_target, **params)
        for setter in _setters: setter.load(_target, _prefix, _settings) #@IgnorePep8

    @staticmethod
    def saveSettings(_target, *_setters, **params):
        (_settings, _prefix) = SettingsFactory._getInitials(_target, **params)
        for setter in _setters: setter.save(_prefix, _settings) #@IgnorePep8

    @staticmethod
    def getSettings(_target, *_setters, **params):
        (_settings, _prefix) = SettingsFactory._getInitials(_target, **params)
        values = [setter.get(_prefix, _settings) for setter in _setters]
        return values[0] if len(values) == 1 else values

    @staticmethod
    def _getInitials(_target, **params):
        return (QSettings(), params.get('_prefix', _target.__class__.__name__))


class Setter(object):
    def __init__(self, **params):
        self.__conv = params.get('_conv', None)
        self.__name = get_other_keys(params, ('_conv',))
        self.__value = params[self.__name]

    def get(self, _prefix, _settings):
        return _settings.value(_prefix + '/' + self.__name,
                QVariant(self.__value) if self.__value else QVariant())

    def set(self, _prefix, _settings):
        value = eval(self.__conv.__name__ + '(' + repr(self.__value) + ')') \
                if self.__conv and self.__value else self.__value
        _settings.setValue(_prefix + '/' + self.__name,
                    QVariant(value) if value else QVariant())

    def load(self, _target, _prefix, _settings):
        value = self.get(_prefix, _settings)
        if self.__conv:  # invoke a conversion
            value = eval('value.' + self.__conv.__name__ + '()')
        # check if self.name exists and it is a method or something callable
        if self.__name in dir(_target) and hasattr(
                            eval('_target.' + self.__name), '__call__'):
            eval('_target.' + self.__name + '(value)')
        else:
            _target.__dict__[self.__name] = value
        return value

    def save(self, _prefix, _settings):
        self.set(_prefix, _settings)
