'''
Created on 23-03-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.misc import Params
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.utils.widgets import PushButtonCommon
    from pygui.qt.utils.widgets import NumberEditCommon
    from pygui.qt.utils.widgets import LabelCommon
    from pymath.time_domain.poincare_plot.filters.square_filter import SquareFilter # @IgnorePep8
    from pygui.qt.custom_widgets.filters.filter_utils import run_filter
except ImportError as error:
    ImportErrorMessage(error, __name__)


class SquareFilterWidget(GroupBoxCommon):
    """
    graphical representation of a square filter
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QHBoxLayout())
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        i18n_def = "Square filter " + self.data_accessor.signal_unit.display_label # @IgnorePep8
        super(SquareFilterWidget, self).__init__(parent, i18n_def=i18n_def,
                                                     **params)

        self.__filter__ = SquareFilter()

        LabelCommon(self, i18n_def="Min value")
        self.__min_value__ = NumberEditCommon(self,
                                        text_handler=self.__min_handler__)
        LabelCommon(self, i18n_def="Max value")
        self.__max_value__ = NumberEditCommon(self,
                                        text_handler=self.__max_handler__)

        self.__button_apply__ = PushButtonCommon(self, i18n_def='Apply',
                                clicked_handler=self.__filter_handler__)
        self.reset()

    def __filter_handler__(self):
        run_filter(self.parent(), self.__filter__, self.data_accessor,
                   filter_name='square')

    def setEnabled(self, _enabled):
        self.__min_value__.setEnabled(_enabled)
        self.__max_value__.setEnabled(_enabled)

    def __min_handler__(self, text):
        self.__filter__.min_value = text
        self.__check_range__(self.__min_value__)

    def __max_handler__(self, text):
        self.__filter__.max_value = text
        self.__check_range__(self.__max_value__)

    def reset(self):
        self.setEnabled(True)
        self.__filter__.reset()
        self.__min_value__.setText(self.__filter__.min_value)
        self.__max_value__.setText(self.__filter__.max_value)

    def __check_range__(self, _widget):
        message = self.__filter__.check()
        if message == None:
            self.__button_apply__.setEnabled(True)
            _widget.setToolTip('')
            self.__button_apply__.setToolTip('')
            return True
        else:
            _widget.setToolTip(message)
            self.__button_apply__.setToolTip(message)
            self.__button_apply__.setEnabled(False)
            return False
