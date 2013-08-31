'''
Created on 21 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_gui.qt.widgets.commons import Common
    from hra_gui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class LabelWidget(QLabel, Common):
    def __init__(self, parent, **params):
        super(LabelWidget, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Preferred)
        prepareWidget(parent=parent, widget=self, textable=True, **params)
