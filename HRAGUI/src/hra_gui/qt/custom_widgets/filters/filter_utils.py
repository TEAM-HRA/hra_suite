'''
Created on 23-03-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_gui.qt.utils.windows import InformationWindow
except ImportError as error:
    ImportErrorMessage(error, __name__)


def run_filter(parent, _filter, _data_accessor, **params):
    """
    function run filter
    """
    message = _filter.check(_data_accessor.data_vector)
    if not message == None:
        InformationWindow(parent, message=message)
        return
    filtered_data = _filter.filter(_data_accessor.data_vector)
    _data_accessor.changeSignal(parent, filtered_data.signal, **params)
    _data_accessor.changeAnnotation(parent, filtered_data.annotation, **params)
