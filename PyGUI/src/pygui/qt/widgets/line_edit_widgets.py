'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.utils.signals import TEXT_CHANGED_SIGNAL
    from pygui.qt.widgets.commons import Common
    from pygui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class LineEditWidget(QLineEdit, Common):
    def __init__(self, parent, **params):
        QLineEdit.__init__(self, parent)
        self.focusEventHandler = params.get('focusEventHandler', None)
        prepareWidget(parent=parent, widget=self, **params)

        text_changed_handler = params.get('text_changed_handler', None)
        if text_changed_handler:
            self.connect(self, TEXT_CHANGED_SIGNAL, text_changed_handler)

    def focusInEvent(self, qfocusevent):
        if not self.focusEventHandler == None:
            self.focusEventHandler()
        super(LineEditWidget, self).focusInEvent(qfocusevent)
