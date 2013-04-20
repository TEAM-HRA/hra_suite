'''
Created on 20 kwi 2013

@author: jurek
'''
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    import pylab as pl
    from pycore.special import ImportErrorMessage
    from pycore.collections_utils import get_or_put
    from pymath.datasources import DataVectorListener
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import GroupBoxCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.widgets import LabelCommon
    from pygui.qt.utils.widgets import SliderCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


class MiscellaneousWidget(GroupBoxCommon):
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

        self.__window_size = __DataWindowSizeWidget__(self,
                                                params.get('data_accessor'))

        self.__use_paramaters__ = CompositeCommon(self, layout=QHBoxLayout())
        self.__use_buffer__ = CheckBoxCommon(self.__use_paramaters__,
                                             i18n_def='Use buffer',
                                             checked=True)
        self.__use_identity_line__ = CheckBoxCommon(self.__use_paramaters__,
                                             i18n_def='Use identity line',
                                             checked=True)

    @property
    def use_buffer(self):
        return self.__use_buffer__.isChecked()

    @property
    def use_identity_line(self):
        return self.__use_identity_line__.isChecked()


class __DataWindowSizeWidget__(CompositeCommon):
    """
    widget used to change data window size
    """
    def __init__(self, parent, data_accessor):
        super(__DataWindowSizeWidget__, self).__init__(parent,
                                            layout=QHBoxLayout())

        self.data_accessor = data_accessor
        self.data_accessor.addListener(self,
                    __DataWindowSizeDataVectorListener__(self))

        LabelCommon(self, i18n_def='Data window size:')

        self.__size_slider__ = SliderCommon(self, orientation=Qt.Horizontal,
                        sizePolicy=QSizePolicy(QSizePolicy.MinimumExpanding,
                                               QSizePolicy.Fixed),
                        value_changed_handler=self.__value_changed__)
        self.__size_slider__.setTickPosition(QSlider.TicksBelow)
        self.changeValue(self.data_accessor.signal)
        self.__size_slider__.setTickInterval(self.__size_slider__.maximum() / 10 ) # @IgnorePep8

        self.__size_value__ = LabelCommon(self, i18n_def='<value>')

    def __value_changed__(self, _value):
        self.__size_value__.setText(str(_value))

    def changeValue(self, _signal):
        self.__size_slider__.setMaximum(int(pl.amax(_signal)))


class __DataWindowSizeDataVectorListener__(DataVectorListener):
    """
    listener to change maximum of data window size slider
    """
    def __init__(self, _data_window_widget):
        self.__data_window_widget__ = _data_window_widget

    def changeAnnotation(self, _annotation, **params):
        self.__data_window_widget__.changeValue(
                    self.__data_window_widget__.data_accessor.signal)

    def changeSignal(self, _signal, **params):
        self.__data_window_widget__.changeValue(_signal)

    def changeXSignalUnit(self, _signal_unit, **params):
        self.__data_window_widget__.changeValue(
                    self.__data_window_widget__.data_accessor.signal)
