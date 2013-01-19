'''
Created on 23-10-2012

@author: jurek
'''

from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QVariant
from pycore.collections import get_other_keys

GLOBAL_SETTINGS = QSettings("med", "med")


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
        return (GLOBAL_SETTINGS,
                params.get('_prefix', _target.__class__.__name__))

    @staticmethod
    def clearSettings():
        GLOBAL_SETTINGS.clear()


class Setter(object):
    def __init__(self, **params):
        self.__conv = params.get('_conv', None)
        self.__no_conv = params.get('_no_conv', False)
        self.__name = get_other_keys(params, ('_conv', 'objectName',
                                              '_conv_2level', '_no_conv'))
        self.__value = params[self.__name]
        self.__object_name = params.get('objectName', '')
        self.__conv_2level = params.get('_conv_2level', None)

    def get(self, _prefix, _settings):
        return _settings.value(self.__id(_prefix),
                QVariant(self.__value) if self.__value else QVariant())

    def set(self, _prefix, _settings):
        if self.__no_conv == True:
            _settings.setValue(self.__id(_prefix), QVariant(self.__value))
        else:
            value = eval(self.__conv.__name__ + '(' + repr(self.__value) + \
                         ')') if self.__conv and self.__value else self.__value
            _settings.setValue(self.__id(_prefix),
                               QVariant(value) if value else QVariant())

    def load(self, _target, _prefix, _settings):
        if not self.__conv and self.__no_conv == False:
            self.__conv = QVariant.toString
        value = self.get(_prefix, _settings)
        if self.__conv and self.__no_conv == False:  # invoke a conversion
            value = eval('value.' + self.__conv.__name__ + '()')

            if isinstance(value, tuple):
                #this means that a tuple has been returned and a real value
                #is stored in the first element, this happens for some
                #converters for example: (int, bool ok) QVariant.toInt(self)
                value = value[0]
        # check if self.name exists and it is a method or something callable
        if self.__name in dir(_target) and hasattr(
                            eval('_target.' + self.__name), '__call__'):
            eval('_target.' + self.__name + '(value)')
        else:
            _target.__dict__[self.__name] = value
            if self.__conv_2level:
                value = self.__conv_2level(value)
                _target.__dict__[self.__name] = value
        return value

    def save(self, _prefix, _settings):
        self.set(_prefix, _settings)

    def __id(self, _prefix):
        return self.__object_name + '/' + _prefix + '/' + self.__name
