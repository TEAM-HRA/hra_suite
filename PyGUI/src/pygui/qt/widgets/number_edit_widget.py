'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.utils.keys import delete_key
    from pygui.qt.utils.keys import movement_key
    from pygui.qt.utils.keys import digit_key
    from pygui.qt.widgets.commons import prepareWidget
    from pygui.qt.widgets.line_edit_widget import LineEditWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class NumberEditWidget(LineEditWidget):
    """
    input text widget which accepts only integer numbers
    """
    def __init__(self, parent, **params):
        super(NumberEditWidget, self).__init__(parent, **params)
        prepareWidget(parent=parent, widget=self, **params)

    def keyPressEvent(self, e):
        key = e.key()
        if delete_key(key) or movement_key(key) or digit_key(key):
            e.accept()
            QLineEdit.keyPressEvent(self, e)
        else:
            e.ignore()

    def setText(self, text):
        super(LineEditWidget, self).setText(str(text))
