'''
Created on 20 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    import pylab as pl
    from pycore.collections_utils import get_or_put
    from pymath.datasources import DataVectorListener
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
    from pygui.qt.widgets.label_widget import LabelWidget
    from pygui.qt.widgets.slider_widget import SliderWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class MiscellaneousWidget(GroupBoxWidget):
    """
    widget used to set up some specific properties like:
    window size,
    using of internal buffer,
    use line of identity
    """
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Miscellaneous')
        super(MiscellaneousWidget, self).__init__(parent, **params)

        LabelWidget(self, i18n_def='Data window shift: 1')
        self.__window_size = __DataWindowSizeWidget__(self,
                                                params.get('data_accessor'))

        self.__use_paramaters__ = CompositeWidget(self, layout=QHBoxLayout())
        self.__use_buffer__ = CheckBoxWidget(self.__use_paramaters__,
                                             i18n_def='Use buffer',
                                             checked=True)
        self.__use_identity_line__ = CheckBoxWidget(self.__use_paramaters__,
                                             i18n_def='Use identity line',
                                             checked=True)

    @property
    def use_buffer(self):
        return self.__use_buffer__.isChecked()

    @property
    def use_identity_line(self):
        return self.__use_identity_line__.isChecked()


class __DataWindowSizeWidget__(CompositeWidget):
    """
    widget used to change data window size
    """
    def __init__(self, parent, data_accessor):
        super(__DataWindowSizeWidget__, self).__init__(parent,
                                            layout=QVBoxLayout())

        self.data_accessor = data_accessor
        self.data_accessor.addListener(self,
                    __DataWindowSizeDataVectorListener__(self))

        info_group = CompositeWidget(self, layout=QHBoxLayout())
        LabelWidget(info_group, i18n_def='Data window size:')
        self.__size_value__ = LabelWidget(info_group, i18n_def='<value>')
        self.__unit_value__ = LabelWidget(info_group, i18n_def='')

        self.__size_slider__ = SliderWidget(self, orientation=Qt.Horizontal,
                        sizePolicy=QSizePolicy(QSizePolicy.MinimumExpanding,
                                               QSizePolicy.Fixed),
                        value_changed_handler=self.__value_changed__)
        self.__size_slider__.setTickPosition(QSlider.TicksBelow)
        self.resetValue()
        self.resetUnit()

    def __value_changed__(self, _value):
        self.__size_value__.setText(str(_value))

    def resetValue(self):
        signal = self.data_accessor.signal_in_x_unit
        self.__size_slider__.setMaximum(int(pl.amax(signal)))
        self.__size_slider__.setValue(0)
        self.__size_slider__.setTickInterval(self.__size_slider__.maximum() / 10 ) # @IgnorePep8

    def resetUnit(self):
        self.__unit_value__.setText(self.data_accessor.signal_x_unit.name)


class __DataWindowSizeDataVectorListener__(DataVectorListener):
    """
    listener to change maximum of data window size slider
    """
    def __init__(self, _data_window_widget):
        self.__data_window_widget__ = _data_window_widget

    def changeAnnotation(self, _annotation, **params):
        self.__data_window_widget__.resetValue()

    def changeSignal(self, _signal, **params):
        self.__data_window_widget__.resetValue()

    def changeXSignalUnit(self, _signal_unit, **params):
        self.__data_window_widget__.resetUnit()
        self.__data_window_widget__.resetValue()
