'''
Created on 21 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_gui.qt.utils.signals import VALUE_CHANGED_SIGNAL
    from hra_gui.qt.widgets.commons import Common
    from hra_gui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class SliderWidget(QSlider, Common):
    def __init__(self, parent, **params):
        super(SliderWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)
        value_changed_handler = params.get('value_changed_handler', None)
        if value_changed_handler:
            self.connect(self, VALUE_CHANGED_SIGNAL, value_changed_handler)
