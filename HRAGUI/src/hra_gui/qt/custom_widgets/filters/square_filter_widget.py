'''
Created on 23-03-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    import collections
    import pylab as pl
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.collections_utils import get_or_put
    from hra_core.misc import Params
    from hra_math.model.data_vector_listener import DataVectorListener
    from hra_gui.qt.widgets.group_box_widget import GroupBoxWidget
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.widgets.number_edit_widget import NumberEditWidget
    from hra_gui.qt.widgets.label_widget import LabelWidget
    from hra_gui.qt.widgets.check_box_widget import CheckBoxWidget
    from hra_gui.qt.utils.windows import InformationWindow
    from hra_math.time_domain.poincare_plot.filters.square_filter import SquareFilter # @IgnorePep8
    from hra_gui.qt.custom_widgets.filters.filter_utils import run_filter
except ImportError as error:
    ImportErrorMessage(error, __name__)

#tuple to collect all parameters of square filter widget in one structure
SquareFilterParams = collections.namedtuple('SquareFilterParams',
                                    ['min_value', 'max_value', 'use_filter'])


class SquareFilterWidget(GroupBoxWidget):
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

        LabelWidget(self, i18n_def="Min value")
        self.__min_value__ = NumberEditWidget(self,
                                    text_changed_handler=self.__min_handler__)
        LabelWidget(self, i18n_def="Max value")
        self.__max_value__ = NumberEditWidget(self,
                                    text_changed_handler=self.__max_handler__)

        if self.params.use_apply_button:
            self.__action_button__ = PushButtonWidget(self, i18n_def='Apply',
                                clicked_handler=self.__filter_handler__)
        else:
            self.__action_button__ = CheckBoxWidget(self,
                            i18n_def='Use filter',
                            clicked_handler=self.__use_handler__)
            self.data_accessor.addListener(self,
                                    __SquareFilterDataVectorListener__(self))
            self.__action_button__.setChecked(False)

        self.reset()

    def __use_handler__(self):
        if not self.params.use_apply_button:
            if not self.isCorrectSignalRange(self.data_accessor.signal):
                self.__action_button__.setChecked(False)

    def __filter_handler__(self):
        if self.isCorrectSignalRange(self.data_accessor.signal):
            run_filter(self.parent(), self.__filter__, self.data_accessor,
                       filter_name='square')

    def isCorrectSignalRange(self, _signal):
        _min = pl.amin(_signal)
        if _min >= self.__filter__.min_value and \
            _min <= self.__filter__.max_value:
            return True
        _max = pl.amax(_signal)
        if _max >= self.__filter__.min_value and \
            _max <= self.__filter__.max_value:
            return True
        if _min <= self.__filter__.min_value and \
            _max >= self.__filter__.max_value:
            return True
        InformationWindow(message="Signal data out of range !")
        return False

    def __min_handler__(self, text):
        self.__filter__.min_value = text
        self.__check_range__(self.__min_value__)

    def __max_handler__(self, text):
        self.__filter__.max_value = text
        self.__check_range__(self.__max_value__)

    def __check_range__(self, _widget):
        message = self.__filter__.check()
        if message == None:
            self.__action_button__.setEnabled(True)
            _widget.setToolTip('')
            self.__action_button__.setToolTip('')
            return True
        else:
            _widget.setToolTip(message)
            self.__action_button__.setToolTip(message)
            self.__action_button__.setEnabled(False)
            if not self.params.use_apply_button:
                self.__action_button__.setChecked(False)
            return False

    def useFilter(self):
        return self.__action_button__.isChecked() \
            if not self.params.use_apply_button else False

    def getFilter(self):
        return self.__filter__

    def reset(self):
        self.setSquareFilterParams(SquareFilterParams(
                                    int(pl.amin(self.data_accessor.signal)),
                                    int(pl.amax(self.data_accessor.signal)),
                                    True))

    def setEnabled(self, _enabled):
        self.__min_value__.setEnabled(_enabled)
        self.__max_value__.setEnabled(_enabled)

    def setSquareFilterParams(self, square_filter_params):
        """
        set up square filter widget parameters
        """
        self.__filter__.min_value = square_filter_params.min_value
        self.__min_value__.setText(self.__filter__.min_value)

        self.__filter__.max_value = square_filter_params.max_value
        self.__max_value__.setText(self.__filter__.max_value)

        if not self.params.use_apply_button:
            self.__action_button__.setChecked(square_filter_params.use_filter)

    def getSquareFilterParams(self):
        return SquareFilterParams(self.__filter__.min_value,
                                  self.__filter__.max_value,
                                  self.useFilter())


class __SquareFilterDataVectorListener__(DataVectorListener):
    """
    class change slave annotation widget if annotation data is changed
    """
    def __init__(self, _filter_widget):
        self.__filter_widget__ = _filter_widget

    def changeAnnotation(self, _annotation, **params):
        self.__reset_signal__(self.__filter_widget__.data_accessor.signal)

    def changeSignal(self, _signal, **params):
        self.__reset_signal__(_signal)

    def __reset_signal__(self, _signal):
        self.__filter_widget__.reset()
