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


class ProgressBarWidget(QProgressBar, Common):
    def __init__(self, parent, **params):
        super(ProgressBarWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)
