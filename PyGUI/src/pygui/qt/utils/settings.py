'''
Created on 23-10-2012

@author: jurek
'''

from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections import get_other_keys
except ImportError as error:
    ImportErrorMessage(error, __name__)

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
    def clearSettings(keys=None):
        if keys == None:
            GLOBAL_SETTINGS.clear()
        else:
            map(GLOBAL_SETTINGS.remove, keys)

    @staticmethod
    def saveObject(object_id, _object):
        #if _object parameter is type of QObject then saving in QSettings
        #repository will failed, so it's much better to throw an exception
        if isinstance(_object, QObject):
            raise TypeError("Type of object for QSettings setValue method can't be QObject type") # @IgnorePep8
        GLOBAL_SETTINGS.setValue(object_id, _object)

    @staticmethod
    def getObjectsForGroup(object_group):
        #in the case when there is a problem to fetch correctly
        #python object from QSettings repository
        #a catch block for exceptions is added
        try:
            return [GLOBAL_SETTINGS.value(key).toPyObject()
                for key in GLOBAL_SETTINGS.allKeys()
                if key.indexOf(object_group) == 0]
        except TypeError:
            return []

    @staticmethod
    def getKeysForGroup(object_group):
        #in the case when there is a problem to fetch correctly
        #python object from QSettings repository
        #a catch block for exceptions is added
        try:
            return [key for key in GLOBAL_SETTINGS.allKeys()
                if key.indexOf(object_group) == 0]
        except TypeError:
            return []


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
