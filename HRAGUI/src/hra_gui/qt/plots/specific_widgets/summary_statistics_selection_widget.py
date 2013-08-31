'''
Created on 04-04-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_core.collections_utils import get_or_put
    from hra_math.statistics.summary_statistics import Asymmetry
    from hra_gui.qt.plots.specific_widgets.statistics_selection_widget import StatisticsSelectionWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class SummaryStatisticsSelectionWidget(StatisticsSelectionWidget):
    """
    widget which gives ability to select summary statistics
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Summary statistics')
        get_or_put(params, 'statistics_base_classes', [Asymmetry])
        super(SummaryStatisticsSelectionWidget, self).__init__(parent,
                                                               **params)
