'''
Created on 21 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.globals import Globals
    from hra_core.introspection import get_object
    from hra_gui.qt.utils.signals import SignalDispatcher
    from hra_gui.qt.utils.signals import EXIT_APPLICATION_SIGNAL
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ApplicationWidget(QApplication):
    def __init__(self, *params):
        super(ApplicationWidget, self).__init__(*params)
        #set up main dispatcher as a QApplication object
        SignalDispatcher.setMainDispatcher(self)

        SignalDispatcher.addSignalSubscriber(self,
                                             EXIT_APPLICATION_SIGNAL,
                                             self.quit)

        #set up USE_NUMPY_EQUIVALENT property
        if not Globals.USE_NUMPY_EQUIVALENT == None:
            NUMPY_UTILS = get_object("hra_math.utils.utils")
            if NUMPY_UTILS:
                if hasattr(NUMPY_UTILS, 'USE_NUMPY_EQUIVALENT'):
                    setattr(NUMPY_UTILS, 'USE_NUMPY_EQUIVALENT',
                            Globals.USE_NUMPY_EQUIVALENT)
