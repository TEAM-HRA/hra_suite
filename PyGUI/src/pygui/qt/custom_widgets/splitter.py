'''
Created on 16-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.settings import SettingsFactory
    from pygui.qt.utils.settings import Setter
    from pygui.qt.utils.widgets import item
    from pygui.qt.utils.widgets import Common
except ImportError as error:
    ImportErrorMessage(error, __name__)


class SplitterWidget(QSplitter, Common):
    def __init__(self, parent, **params):
        QSplitter.__init__(self, parent)
        item(parent=parent, widget=self, **params)
        self.params = Params(**params)
        self.setHandleWidth(self.handleWidth() * 2)
        if self.params.save_state:
            SettingsFactory.loadSettings(self,
                    Setter(sizes_list=None,
                           _conv=QVariant.toPyObject,
                           _conv_2level=self.conv2level,
                           objectName=self.params.objectName
                           ))

    def saveSettings(self):
        if self.params.save_state:
            SettingsFactory.saveSettings(self,
                                         Setter(sizes_list=self.sizes(),
                                            _no_conv=True,
                                            objectName=self.params.objectName))

    def conv2level(self, value):
        return None if value == None else [variant.toInt()[0]
                                           for variant in value]

    def sizesLoaded(self):
        return not self.sizes_list == None and len(self.sizes_list) > 0

    def updateSizes(self):
        if self.sizesLoaded():
            self.setSizes(self.sizes_list)
