'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.utils.windows import InformationWindow
except ImportError as error:
    ImportErrorMessage(error, __name__)


def run_filter(parent, _filter, _data_accessor, _excluded_annotations=None):
    """
    function run filter
    """
    if _excluded_annotations:
        message = _filter.check(_data_accessor.data_vector,
                                _excluded_annotations)
    else:
        message = _filter.check(_data_accessor.data_vector)
    if not message == None:
        InformationWindow(parent, message=message)
        return
    if _excluded_annotations:
        filtered_data = _filter.filter(_data_accessor.data_vector,
                                       _excluded_annotations)
    else:
        filtered_data = _filter.filter(_data_accessor.data_vector)
    _data_accessor.changeSignal(parent, filtered_data.signal)
    _data_accessor.changeAnnotation(parent, filtered_data.annotation)
