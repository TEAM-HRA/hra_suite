'''
Created on 05-01-2013

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from pycommon.plugins_parser import PluginsBuilder
from pycore.globals import GLOBALS  # @UnusedImport
from pygui.qt.utils.specials import getWidgetFromStack
from pycore.misc import Params


class PluginsNames(object):
    POINCARE_PLOT_PLUGIN_NAME = 'poincare'


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
                    if param.key:
                        _params.append(getattr(local_params, param.key))
                    elif param.value:
                        _params.append(param.value)
                if len(params) > 0:
                    self.__host_stack_object__.emit(signal.resolveIdent,
                                                    *_params)
                else:
                    self.__host_stack_object__.emit(signal.resolveIdent)
