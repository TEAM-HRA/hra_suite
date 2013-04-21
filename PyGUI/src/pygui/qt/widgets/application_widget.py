'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.globals import Globals
    from pycore.introspection import get_object
    from pygui.qt.utils.signals import SignalDispatcher
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ApplicationWidget(QApplication):
    def __init__(self, *params):
        super(ApplicationWidget, self).__init__(*params)
        #set up main dispatcher as a QApplication object
        SignalDispatcher.setMainDispatcher(self)

        #set up USE_NUMPY_EQUIVALENT property
        if not Globals.USE_NUMPY_EQUIVALENT == None:
            NUMPY_UTILS = get_object("pymath.utils.utils")
            if NUMPY_UTILS:
                if hasattr(NUMPY_UTILS, 'USE_NUMPY_EQUIVALENT'):
                    setattr(NUMPY_UTILS, 'USE_NUMPY_EQUIVALENT',
                            Globals.USE_NUMPY_EQUIVALENT)
