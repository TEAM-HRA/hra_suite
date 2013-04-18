'''
Created on 11 kwi 2013

@author: jurek
'''

from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
except ImportError as error:
    ImportErrorMessage(error, __name__)


def movement_key(key):
    """
    returns true if a key is type of a movement key
    """
    if key == Qt.Key_Backspace:
        pass
    elif key == Qt.Key_Left:
        pass
    elif key == Qt.Key_Right:
        pass
    elif key == Qt.Key_End:
        pass
    elif key == Qt.Key_Home:
        pass
    elif key == Qt.Key_Tab:
        pass
    else:
        return False
    return True


def digit_key(key):
    """
    returns true if a key is type of a digit key
    """
    return key >= Qt.Key_0 and key <= Qt.Key_9


def delete_key(key):
    """
    returns true if a key is DEL key
    """
    return key == Qt.Key_Delete
