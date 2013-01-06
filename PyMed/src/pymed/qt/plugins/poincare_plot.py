'''
Created on 05-01-2013

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycore.misc import Params


class PoincareTabWidget(QWidget):
    """
    only for test purpose
    """
    def __init__(self, **params):
        self.params = Params(**params)
        QWidget.__init__(self, parent=self.params.parent)
        #self.setParent(_parent)
        self.setLayout(QHBoxLayout())
        #_parent.layout().addWidget(composite)

        clearButton = QPushButton("Clear", self)
        self.layout().addWidget(clearButton)
