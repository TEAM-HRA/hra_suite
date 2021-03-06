'''
Created on 05-01-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_common.plugins_parser import PluginsBuilder
    from hra_core.globals import GLOBALS  # @UnusedImport
    from hra_core.collections_utils import get_subdict
    from hra_gui.qt.utils.specials import getWidgetFromStack
    from hra_core.misc import Params
    from hra_gui.qt.activities.activities import ActivityManager
    from hra_gui.qt.activities.activities import PluginActivity
except ImportError as error:
    ImportErrorMessage(error, __name__)


class PluginsNames(object):
    TACHOGRAM_PLOT_PLUGIN_NAME = 'tachogram'


class PluginsManager(object):

    @staticmethod
    def invokePlugin(_plugin_ident, _stack, **params):
        __Plugin__(_plugin_ident, _stack).invoke(**params)


class __Plugin__(object):

    def __init__(self, _plugin_ident, _stack):
        self.__ident__ = _plugin_ident
        self.__host_stack_object__ = None

        self.__plugin__ = PluginsBuilder.getPlugin(self.__ident__)
        if self.__plugin__:
            self.__host_stack_object__ = getWidgetFromStack(_stack,
                                        self.__plugin__.resolveHostObjectName)

    def invoke(self, **params):
        local_params = Params(**params)
        if self.__plugin__ == None:
            return
        if self.__host_stack_object__ == None:
            return

        if self.__host_stack_object__:
            for signal in self.__plugin__.signals:
                _params = []
                for param in signal.params:
                    if not param.key == None:
                        _params.append(getattr(local_params, param.key))
                    elif not param.value == None:
                        if param.value.title() in ('True', 'False'):
                            _params.append(param.value.title() == 'True')
                        elif param.value == "None":
                            _params.append(None)
                        else:
                            _params.append(param.value)
                if local_params.activity_description \
                    and local_params.activity_params:
                    ActivityManager.saveActivity(PluginActivity(self.__ident__,
                        description=local_params.activity_description,
                        **get_subdict(params,
                                      keys=local_params.activity_params)))
                if len(params) > 0:
                    self.__host_stack_object__.emit(signal.resolveIdent,
                                                    *_params)
                else:
                    self.__host_stack_object__.emit(signal.resolveIdent)
