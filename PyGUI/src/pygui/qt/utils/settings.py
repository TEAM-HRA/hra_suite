'''
Created on 23-10-2012

@author: jurek
'''

from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.collections_utils import get_other_keys
except ImportError as error:
    ImportErrorMessage(error, __name__)

GLOBAL_SETTINGS = QSettings("med", "med")
DEFAULT_SETTINGS_GROUP = 'settings'

TEMPORARY_SETTINGS_GROUP = 'temp'
TEMPORARY_SETTINGS_ID = 'TEMPORARY_SETTINGS_ID'
TEMPORARY_SAVE_SETTINGS_METHOD = 'saveTemporarySettings'


class SettingsFactory(object):
    @staticmethod
    def loadSettings(_target, *_setters, **params):
        (_settings, _prefix) = SettingsFactory._getInitials(_target, **params)
        return [setter.load(_target, _prefix, _settings) for setter in _setters] #@IgnorePep8

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
        settings_id = params.get(TEMPORARY_SETTINGS_ID, '')
        return (GLOBAL_SETTINGS,
            params.get('_prefix', _target.__class__.__name__ + settings_id))

    @staticmethod
    def clearSettings(keys_or_object_group=None):
        if keys_or_object_group == None:
            GLOBAL_SETTINGS.clear()
        else:
            if isinstance(keys_or_object_group, list):
                map(GLOBAL_SETTINGS.remove, keys_or_object_group)
            else:
                SettingsFactory.clearSettings(
                        SettingsFactory.getKeysForGroup(keys_or_object_group))

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

    @staticmethod
    def loadTemporarySettings(_target, settings_id, *_setters, **params):
        params['settings_group'] = TEMPORARY_SETTINGS_GROUP
        params[TEMPORARY_SETTINGS_ID] = settings_id
        return SettingsFactory.loadSettings(_target, *_setters, **params)

    @staticmethod
    def saveTemporarySettings(_target, settings_id, *_setters, **params):
        params['settings_group'] = TEMPORARY_SETTINGS_GROUP
        params[TEMPORARY_SETTINGS_ID] = settings_id
        SettingsFactory.saveSettings(_target, *_setters, **params)


class Setter(object):
    def __init__(self, **params):
        self.__conv = params.get('_conv', None)
        self.__no_conv = params.get('_no_conv', False)
        self.__name = get_other_keys(params, ('_conv', 'objectName',
                                              '_conv_2level', '_no_conv',
                                              'settings_group', '_use_only_value',  # @IgnorePep8
                                              '_handlers')) # @IgnorePep8
        self.__value = params[self.__name]
        self.__object_name = params.get('objectName', '')
        self.__conv_2level = params.get('_conv_2level', None)
        self.__settings_group__ = params.get('settings_group',
                                             DEFAULT_SETTINGS_GROUP)
        self.__use_only_value = params.get('_use_only_value', False)
        self.__handlers = params.get('_handlers', None)

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
        if self.__use_only_value:
            if self.__conv_2level:
                value = self.__conv_2level(value)
        else:
            # check if self.name exists and it is a method or something
            # callable
            if self.__name in dir(_target) \
                and hasattr(eval('_target.' + self.__name), '__call__'):
                eval('_target.' + self.__name + '(value)')
            else:
                _target.__dict__[self.__name] = value
                if self.__conv_2level:
                    value = self.__conv_2level(value)
                    _target.__dict__[self.__name] = value
        if not self.__handlers == None:
            for handler in self.__handlers:
                handler(value)
        return value

    def save(self, _prefix, _settings):
        self.set(_prefix, _settings)

    def __id(self, _prefix):
        return '/'.join([self.__settings_group__, self.__object_name,
                         _prefix, self.__name])

    def useOnlyValue(self, use_only_value):
        self.__use_only_value = use_only_value

    def setNoConv(self, _no_conv):
        self.__no_conv = _no_conv


def set_temporary_settings_id(target):
    """
    function set a new property to mark temporary settings id
    """
    setattr(target, TEMPORARY_SETTINGS_ID, str(id(target)))

#if client class code implements getTemporarySetters, then it us used in
#TemporarySettingsHandler.hideEvent method
TEMPORARY_GET_TEMPORARY_SETTERS_METHOD = 'getTemporarySetters'


class TemporarySettingsHandler(QWidget):
    """
    class used to save and load temporary settings
    """
    def __init__(self, parent, *params_l, **params_d):
        super(TemporarySettingsHandler, self).__init__(parent, *params_l,
                                                       **params_d)
        self.__settings_id__ = None

        #the self object could implement two methods
        if hasattr(self, TEMPORARY_SAVE_SETTINGS_METHOD) or \
            hasattr(self, TEMPORARY_GET_TEMPORARY_SETTERS_METHOD):
            #the following loop search for any parent object which
            #have property TEMPORARY_SETTINGS_ID, if that is the case
            #this identifier is set up for a current object
            while not parent == None:
                if hasattr(parent, TEMPORARY_SETTINGS_ID):
                    self.__settings_id__ = str(getattr(parent,
                                                       TEMPORARY_SETTINGS_ID))
                    break
                else:
                    if hasattr(parent, 'parent'):
                        parent = parent.parent()
                    else:
                        break

    def hideEvent(self, event):
        """
        if a widget is hiding all settings are saved
        """
        if not self.__settings_id__ == None:
            if hasattr(self, TEMPORARY_SAVE_SETTINGS_METHOD):
                method = getattr(self, TEMPORARY_SAVE_SETTINGS_METHOD)
                method()
            elif hasattr(self, TEMPORARY_GET_TEMPORARY_SETTERS_METHOD):
                self.saveTemporarySettingsHandler(self.getTemporarySetters(),
                                              _no_conv=True)
        super(TemporarySettingsHandler, self).hideEvent(event)

    def loadTemporarySettingsHandler(self, setters, use_only_value=True):
        """
        loads temporary settings identified by collections of setters;
        by default values fetched from settings storage are returned
        not set as properties of the host object
        """
        if not self.__settings_id__ == None:
            for setter in setters:
                setter.useOnlyValue(use_only_value)
            return SettingsFactory.loadTemporarySettings(self,
                                            self.__settings_id__, *setters)

    def saveTemporarySettingsHandler(self, setters, _no_conv=False):
        """
        saves temporary settings identified by collections of setters
        """
        if not self.__settings_id__ == None:
            if _no_conv:
                for setter in setters:
                    setter.setNoConv(True)
            SettingsFactory.saveTemporarySettings(self,
                                            self.__settings_id__, *setters)
