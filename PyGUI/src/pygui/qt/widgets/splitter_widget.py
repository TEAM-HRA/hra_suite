'''
Created on 16-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.collections_utils import get_or_put
    from pygui.qt.utils.settings import SettingsFactory
    from pygui.qt.utils.settings import Setter
    from pygui.qt.widgets.commons import prepareWidget
    from pygui.qt.widgets.commons import Common
except ImportError as error:
    ImportErrorMessage(error, __name__)


class SplitterWidget(QSplitter, Common):
    def __init__(self, parent, **params):
        get_or_put(params, 'orientation', Qt.Horizontal)
        self.params = Params(**params)
        QSplitter.__init__(self, self.params.orientation, parent=parent)
        prepareWidget(parent=parent, widget=self, **params)
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
        if not value == None:
            #this is a little strange code, the first invocation of the method
            #gets QVariant object of QStringList type, every next one
            #gets QVariant object of QVariantList type obtained from QSettings,
            #that's why there is a check for existence of toInt method;
            #this is very odd behaviour
            return [variant.toInt()[0] if hasattr(variant, 'toInt')
                    else variant for variant in value]

    def sizesLoaded(self):
        return not self.sizes_list == None and len(self.sizes_list) > 0

    def updateSizes(self):
        if self.sizesLoaded():
            self.setSizes(self.sizes_list)

    def changeSplitterHandleColor(self, idx, color):
        """
        method used to change color of specified (by idx) handle splitter
        """
        handle = self.handle(idx)
        p = handle.palette()
        p.setColor(handle.backgroundRole(), color)
        handle.setPalette(p)
        handle.setAutoFillBackground(True)
