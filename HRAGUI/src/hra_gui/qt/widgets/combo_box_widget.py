'''
Created on 21 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_gui.qt.utils.signals import CURRENT_INDEX_CHANGED_SIGNAL
    from hra_gui.qt.widgets.commons import Common
    from hra_gui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ComboBoxWidget(QComboBox, Common):
    def __init__(self, parent, **params):
        super(ComboBoxWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)
        click_handler = params.get('clicked_handler', None)
        if click_handler:
            self.connect(self, CURRENT_INDEX_CHANGED_SIGNAL, click_handler)
