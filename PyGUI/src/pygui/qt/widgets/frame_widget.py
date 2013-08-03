'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.widgets.commons import Common
    from pygui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class FrameWidget(QFrame, Common):
    """
    an equivalent of QFrame widget
    """
    def __init__(self, parent, **params):
        super(FrameWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)
