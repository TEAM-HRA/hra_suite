'''
Created on Jul 20, 2013

@author: jurek
'''

from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import ColorRGB
except ImportError as error:
    ImportErrorMessage(error, __name__)


def get_color_RGB(colour):
    """
    function converts color as a QColor object into ColorRGB object
    """
    qcolour = QColor(colour)
    return ColorRGB(qcolour.red(), qcolour.green(), qcolour.blue())
