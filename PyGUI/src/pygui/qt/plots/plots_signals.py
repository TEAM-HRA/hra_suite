'''
Created on 25-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
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
#signal emitted when tachogram plot settings;
#the first parameter is unit of x axis, the second is window id
SHOW_TACHOGRAM_PLOT_SETTINGS = SIGNAL('show_tachogram_plot_settings(PyQt_PyObject)') # @IgnorePep8
#signal emitted when x unit of tachogram plot is about to change;
#the first parameter is unit of x axis
CHANGE_X_UNIT_TACHOGRAM_PLOT_SIGNAL = SIGNAL('change_x_unit_tachogram_plot(PyQt_PyObject)') # @IgnorePep8
