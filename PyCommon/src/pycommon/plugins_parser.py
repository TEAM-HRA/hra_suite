'''
Created on 20-10-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from xml.sax import make_parser
    from xml.sax import ContentHandler
    from xml.sax import SAXParseException
    from pycore.misc import camel_format
    from pycore.resources import get_as_resource_handler_or_string
    from pycore.globals import GLOBALS
    from pycore.introspection import get_object
except ImportError as error:
    ImportErrorMessage(error, __name__)


class Plugin(object):
    """
    a class which represents a plugin tag
    """
    def __init__(self):
        self.__ident__ = None
        self.__host_object_name__ = None
        self.__signals__ = []

    @property
    def ident(self):
        return self.__ident__

    @property
    def resolveIdent(self):
        return get_object(self.__ident__, self.__ident__)

    @ident.setter
    def ident(self, _ident):
        self.__ident__ = _ident

    @property
    def resolveHostObjectName(self):
        return get_object(self.__host_object_name__, self.__host_object_name__)

    @property
    def hostObjectName(self):
        return self.__host_object_name__

    @hostObjectName.setter
    def hostObjectName(self, _host_object_name):
        self.__host_object_name__ = _host_object_name

    @property
    def signals(self):
        return self.__signals__

    @signals.setter
    def signals(self, _signals):
        self.__signals__ = _signals


class Signal(object):
    """
    a class which represents a signal tag (subtag of plugin tag)
    """
    def __init__(self):
        self.__ident__ = None
        self.__params__ = []

    @property
    def ident(self):
        return self.__ident__

    @property
    def resolveIdent(self):
        return get_object(self.__ident__, self.__ident__)

    @ident.setter
    def ident(self, _ident):
        self.__ident__ = _ident

    @property
    def params(self):
        return self.__params__

    @params.setter
    def params(self, _params):
        self.__params__ = _params


class Param(object):
    """
    a class which represents a param tag (subtag of signal tag)
    """
    def __init__(self):
        self.__value__ = None
        self.__key__ = None

    @property
    def value(self):
        return self.__value__

    @value.setter
    def value(self, _value):
        self.__value__ = _value

    @property
    def key(self):
        return self.__key__

    @key.setter
    def key(self, _key):
        self.__key__ = _key


class PluginsBuilder(object):
    """
    a tool class to parse plugins configuration files,
    used by a client code to get a plugin specification
    for based on plugin id
    """
    __BUILDER__ = None

    def __init__(self):
        self.__handler__ = None
        self.__plugins__ = None

    def parse(self, filename_or_resource):
        try:
            self.__handler__ = __PluginsHandler__()
            parser = make_parser()
            parser.setContentHandler(self.__handler__)
            parser.parse(filename_or_resource)
            return True
        except (EnvironmentError, ValueError, SAXParseException) as err:
            print(err)
            return False

    def getHandler(self):
        return self.__handler__

    @staticmethod
    def getPlugin(plugin_ident):
        if PluginsBuilder.__BUILDER__ == None:
            builder = PluginsBuilder()
            builder.parse(get_as_resource_handler_or_string(
                                                        GLOBALS.PLUGINS_FILE))
            PluginsBuilder.__BUILDER__ = builder
        return PluginsBuilder.__BUILDER__.getHandler().getPlugin(plugin_ident)


class __PluginsHandler__(ContentHandler):
    """
    a content parser for plugins configuration files
    """
    __PLUGIN_TAG__ = "plugin"
    __SIGNALS_TAG__ = "signals"
    __SIGNAL_TAG__ = "signal"
    __PARAMS_TAG__ = "params"
    __PARAM_TAG__ = "param"

    def __init__(self):
        ContentHandler.__init__(self)
        self.__plugins__ = []
        self.__signals__ = []
        self.__params__ = []
        self.__plugins_map__ = None

    def startElement(self, name, attributes):
        if name == __PluginsHandler__.__PLUGIN_TAG__:
            plugin = Plugin()
            for key, value in attributes.items():
                plugin.__setattr__(camel_format(key), value)
            self.__plugins__.append(plugin)

        elif name == __PluginsHandler__.__SIGNALS_TAG__:
            self.__signals__[:] = []
        elif name == __PluginsHandler__.__SIGNAL_TAG__:
            signal = Signal()
            for key, value in attributes.items():
                signal.__setattr__(camel_format(key), value)
            self.__signals__.append(signal)

        elif name == __PluginsHandler__.__PARAMS_TAG__:
            self.__params__[:] = []
        elif name == __PluginsHandler__.__PARAM_TAG__:
            param = Param()
            for key, value in attributes.items():
                param.__setattr__(camel_format(key), value)
            self.__params__.append(param)

    def endElement(self, name):
        if name == __PluginsHandler__.__SIGNALS_TAG__:
            self.__plugins__[len(self.__plugins__) - 1].signals = \
                                                            self.__signals__
        elif name == __PluginsHandler__.__PARAMS_TAG__:
            self.__signals__[len(self.__signals__) - 1].params = \
                                                            self.__params__

    def getPlugin(self, plugin_ident):
        if self.__plugins_map__ == None:
            self.__plugins_map__ = {}
            for plugin in self.__plugins__:
                self.__plugins_map__[plugin.resolveIdent] = plugin
        return self.__plugins_map__.get(plugin_ident, None)
