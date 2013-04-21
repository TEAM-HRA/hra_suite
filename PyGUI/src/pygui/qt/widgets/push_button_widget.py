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


class PushButtonWidget(QPushButton, Common):
    def __init__(self, parent, **params):
        super(PushButtonWidget, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                               QSizePolicy.Fixed)
        prepareWidget(parent=parent, widget=self, textable=True, **params)
