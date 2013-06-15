'''
Created on 23-10-2012

@author: jurek
'''

from pycore.special import ImportErrorMessage
try:
    import functools
    import inspect
    from types import MethodType
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.collections_utils import get_other_keys
except ImportError as error:
    ImportErrorMessage(error, __name__)

GLOBAL_SETTINGS = QSettings("med", "med")
DEFAULT_SETTINGS_GROUP = 'settings'

TEMPORARY_SETTINGS_GROUP = 'temp'
TEMPORARY_SETTINGS_ID = 'TEMPORARY_SETTINGS_ID'


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
        if not self.__name == None:
            self.__value = params[self.__name]
        self.__object_name = params.get('objectName', '')
        self.__conv_2level = params.get('_conv_2level', None)
        self.__settings_group__ = params.get('settings_group',
                                             DEFAULT_SETTINGS_GROUP)
        self.__use_only_value = params.get('_use_only_value', False)
        self.__handlers = params.get('_handlers', None)

    def set_value(self, name, value=None):
        self.__name = name
        self.__value = value

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

            if isinstance(value, tuple) and \
                not self.__conv == QVariant.toPyObject:
                #this means that a tuple has been returned and a real value
                #is stored in the first element, this happens for some
                #converters for example: (int, bool ok) QVariant.toInt(self)
                #the case of QVariant.toPyObject have to be excluded to give
                #ability to save and restore user defined tuples
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


class __Params__(object):
    """
    class to store parameters for Setter class
    """
    def __init__(self, name, _conv=None, _conv_2level=None,
                 _setter_handler=None, _getter_handler=None,
                 before_name=None):
        self.name = name
        self._conv = _conv
        self.setter_handler = _setter_handler
        self.getter_handler = _getter_handler
        self._conv_2level = _conv_2level
        self.before_name = before_name


def hideEvent(_self, event):
    """
    this function is attached to a widget to save
    some properties when a widget is hidden
    """
    setters = []
    for setter_params in _self.__setters_params__:

        #this code is very important setter_params.setter_handler and
        #setter_params.getter_handler are unbound functions, to use
        #them as methods of _self object they have to be bounded
        getter_handler = None
        if not setter_params.getter_handler == None:
            getter_handler = setter_params.getter_handler.__get__(
                                            _self, _self.__class__)
        setter = Setter()
        if not getter_handler == None:
            setter.set_value(setter_params.name, getter_handler())
        else:
            setter.set_value(setter_params.name)
        setter.setNoConv(True)
        setters.append(setter)

    SettingsFactory.saveTemporarySettings(_self, _self.__settings_id__,
                                          *setters)
    super(_self.__class__, _self).hideEvent(event)


class temporarySettingsDecorator(object):
    """
    this a constructor decorator to load previously saved settings
    """

    def __call__(self, _init, *args, **kargs):

        def wrapper(_self, *args, **kargs):

            _init(_self, *args, **kargs)

            settings_id = None
            parent = args[0] if len(args) > 0 else None

            #the following loop searches for a settings id of any parent
            #of _self object
            while not parent == None:
                if hasattr(parent, TEMPORARY_SETTINGS_ID):
                    settings_id = str(getattr(parent,
                                              TEMPORARY_SETTINGS_ID))
                    break
                else:
                    if hasattr(parent, 'parent'):
                        parent = parent.parent()
                    else:
                        break
            if settings_id == None:
                return

            setattr(_self, '__settings_id__', settings_id)

            setters = []
            #search only for members (methods) which have been attached
            #by temporarySetterDecorator decorator to _self object
            setters_params = [member[1].setter_params
                    for member in inspect.getmembers(_self, inspect.ismethod)
                                        if hasattr(member[1], 'setter_params')]

            #if there is any setter param before_name properties defined
            #in setter params objects then setters_params list
            #have to be reordered
            setters_params = self.__reorder_setters_params__(setters_params)

            for setter_params in setters_params:

                #this code is very important: setter_params.setter_handler and
                #setter_params.getter_handler are unbound functions,
                #as a result of use of temporarySetterDecorator on methods
                #of _self object; to convert them into bounded methods of
                #_self object the following code is used (__get__ method)
                setter_handler = None
                if not setter_params.setter_handler == None:
                    setter_handler = setter_params.setter_handler.__get__(
                                                    _self, _self.__class__)
                getter_handler = None
                if not setter_params.getter_handler == None:
                    getter_handler = setter_params.getter_handler.__get__(
                                                    _self, _self.__class__)

                #create setter object based on parameters fetched from
                #setter params object
                setter = Setter(_conv=setter_params._conv \
                                    if setter_params._conv else None,
                                _conv_2level=setter_params._conv_2level \
                                    if setter_params._conv_2level else None,
                                _handlers=[setter_handler] \
                                    if setter_handler else None)
                if not getter_handler == None:
                    setter.set_value(setter_params.name, getter_handler())
                else:
                    setter.set_value(setter_params.name)
                setter.useOnlyValue(True)
                setters.append(setter)

            if len(setters_params) > 0:
                #load previously saved settings
                SettingsFactory.loadTemporarySettings(_self, settings_id,
                                                      *setters)

                #save setter params objects to be later used in hideEvent
                #method
                setattr(_self, '__setters_params__', setters_params)

                #attached hideEvent method to _self object at runtime
                _self.hideEvent = MethodType(hideEvent, _self, _self.__class__)

        return wrapper

    def __reorder_setters_params__(self, setters_params):
        """
        method changes order of setters params list if there is
        before_name property in any of the setter params items
        included in the list
        """
        ordered_names = []
        reorder = False
        for setter_params in setters_params:
            if not setter_params.before_name == None:
                if ordered_names.count(setter_params.before_name) > 0:
                    name_idx = ordered_names.index(setter_params.before_name)
                    ordered_names.insert(name_idx, setter_params.name)
                    reorder = True
                    continue
            ordered_names.append(setter_params.name)

        if reorder:
            ordered_setters_params = []
            for name in ordered_names:
                ordered_setters_params.append([setter_params
                                        for setter_params in setters_params
                                            if setter_params.name == name][0])
            return ordered_setters_params
        else:
            return setters_params


def temporarySetterDecorator(**kargs):
    """
    a function decorator used to mark a setter member of a host widget
    which will be an engine during of saving process;
    the decorator accepts the following arguments:
    name - to identify the property
    _conf - (optional) a conversion function
    _setter_handler - a decorated method itself
    _getter_handler - a corresponding getter handler
    before_name - (optional) define a setter param name before which
                this setter param has to be placed, this happens in runtime
    """

    def wrapper_setter(_method):
        # make a new function
        @functools.wraps(_method)
        def wrapper(_self, _value):
            return _method(_self, _value)

        setter_params = __Params__(name=kargs.get('name'),
                            _conv=kargs.get('_conv', None),
                            _conv_2level=kargs.get('_conv_2level', None),
                            _setter_handler=wrapper,
                            _getter_handler=kargs.get('_getter_handler', None),
                            before_name=kargs.get('before_name', None))
        #this cyclic reference between wrapped function and setter params
        #object is intentional to get all needed information from setter
        #params object attached to decorated method, the means:
        #name, conversion method, setter handler and wrapper (setter) method
        wrapper.setter_params = setter_params
        return wrapper
    return wrapper_setter
