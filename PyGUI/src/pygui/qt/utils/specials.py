'''
Created on 25-12-2012

@author: jurek

Module with some special functionality which couldn't appear in other
modules because occurrence of, for example, cycling imports
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
import inspect
from pycore.globals import GLOBALS

#global cache for objects founded by __getObjectFromStack__(...) method
__STACK_OBJECTS__ = {}


class StackObject(object):
    NONE = 0
    NEW = 1
    EXISTS = 2
    ANY = 3

    def __init__(self, obj, status=NONE):
        if isinstance(obj, StackObject):
            self._object = obj._object
        else:
            self._object = obj
        self.status = status


def getWidgetFromStack(stack=inspect.stack(), widget_name=None):
    return __getObjectFromStack__(stack,
                        QWidget if widget_name == None else widget_name)


def getMainWindowFromStack(stack=inspect.stack()):
    return __getObjectFromStack__(stack, QMainWindow)


def getOrCreateTabFromMainTabWidgetStack(tabName, stack=inspect.stack(),
                                         layout=None):
    tabWidget = getWidgetFromStack(stack, GLOBALS.WORKSPACE_NAME)
    if not tabWidget == None:
        for idx in range(tabWidget.count()):
            if tabWidget.tabText(idx) == tabName:
                return StackObject(tabWidget.widget(idx), StackObject.EXISTS)
        tab = QWidget(tabWidget)
        if not layout == None:
            tab.setLayout(layout)
        tabWidget.addTab(tab, tabName)
        return StackObject(tab, StackObject.NEW)
    else:
        tab = getWidgetFromStack(stack)
        return StackObject(tab, StackObject.ANY)


def __getObjectFromStack__(stack, class_or_object_name):
    """
    method returns object acquired from stack
    """
    obj_ = __STACK_OBJECTS__.get(str(class_or_object_name), None)
    if not obj_ == None:
        return obj_
    for _stack in stack:
        frame = _stack[0]
        locals_ = frame.f_locals
        for key in locals_:
            obj_ = locals_.get(key)
            #if parameter is a kind of string
            if hasattr(class_or_object_name, '__len__'):
                (ok, obj_) = __get_object_for_object_name__(obj_,
                                                 class_or_object_name)
                if ok == 0:
                    continue
            elif not isinstance(obj_, class_or_object_name):
                continue
            __STACK_OBJECTS__[str(class_or_object_name)] = obj_
            return obj_


def __get_object_for_object_name__(obj, object_name):
    """
    method which returns object with specified object_name,
    searching over all properties of the parameter object obj
    """
    if isinstance(obj, QObject) and obj.objectName() == object_name:
        return (1, obj)
    for name in dir(obj):
        if hasattr(obj, name):
            value = getattr(obj, name)
            if isinstance(value, QObject) and value.objectName() == object_name: # @IgnorePep8
                return (1, value)
    return (0, None)
