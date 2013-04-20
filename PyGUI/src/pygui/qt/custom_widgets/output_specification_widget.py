'''
Created on 19 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.custom_widgets.decimal_precision_widget import DecimalPrecisionWidget # @IgnorePep8
    from pygui.qt.custom_widgets.separator_widget import SeparatorWidget # @IgnorePep8
    from pygui.qt.custom_widgets.dir_widget import DirWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class OutputSpecificationWidget(GroupBoxCommon):
    """
    widget used to specify output parameters like:
    output dir,
    output data precision,
    output data separator,
    whether skip existing outcomes
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Output specification')
        super(OutputSpecificationWidget, self).__init__(parent, **params)
        self.__output_dir__ = DirWidget(self)
        self.__precision__ = DecimalPrecisionWidget(self)
        self.__separator__ = SeparatorWidget(self, i18n_def='Output separator')
        self.__skip_existing__ = CheckBoxCommon(self, i18n_def='Skip existing outcomes') # @IgnorePep8