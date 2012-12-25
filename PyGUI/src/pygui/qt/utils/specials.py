'''
Created on 25-12-2012

@author: jurek

Module with some special functionality which couldn't appear in other
modules because occurrence of, for example, cycling imports
'''
from PyQt4.QtGui import QWidget


def getWidgetFromStack(stack):
    """
    method returns QWidget object, any first encountered,
    acquired from stack object
    """
    for _stack in stack:
        frame = _stack[0]
        locals_ = frame.f_locals
        for key in locals_:
            obj_ = locals_.get(key)
            if isinstance(obj_, QWidget):
                return obj_
