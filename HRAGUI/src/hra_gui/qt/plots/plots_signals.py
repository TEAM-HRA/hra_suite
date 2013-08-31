'''
Created on 25-03-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
except ImportError as error:
    ImportErrorMessage(error, __name__)

#signal emitted to maximize tachogram plot
MAXIMIZE_TACHOGRAM_PLOT_SIGNAL = SIGNAL('maximize_tachogram_plot()')

#signal emitted to restore tachogram plot
RESTORE_TACHOGRAM_PLOT_SIGNAL = SIGNAL('restore_tachogram_plot()')

#signal emitted to close tachogram plot
CLOSE_TACHOGRAM_PLOT_SIGNAL = SIGNAL('close_tachogram_plot(PyQt_PyObject)')
