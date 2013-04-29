'''
Created on 20 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    import pylab as pl
    from pycore.misc import Params
    from pycore.units import OrderUnit
    from pycore.collections_utils import get_or_put
    from pymath.model.data_vector_listener import DataVectorListener
    from pymath.model.data_vector_parameters import DataVectorParameters
    from pymath.time_domain.poincare_plot.poincare_plot_parameters import PoincarePlotParameters # @IgnorePep8
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
    from pygui.qt.widgets.label_widget import LabelWidget
    from pygui.qt.widgets.slider_widget import SliderWidget
    from pygui.qt.custom_widgets.units import TimeUnitsWidget
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
        self.params = Params(**params)
        self.params.data_accessor.addListener(self,
                                    __MiscellaneousVectorListener__(self))
        self.__window_size__ = __DataWindowSizeWidget__(self,
                                                self.params.data_accessor)

        self.__unitsWidget__ = TimeUnitsWidget(self, i18n_def='Units',
                        default_unit=self.params.data_accessor.signal_x_unit,
                        change_unit_handler=self.changeUnit,
                        layout=QHBoxLayout())
        self.__unitsWidget__.addUnit(OrderUnit)

        self.__use_parameters__ = CompositeWidget(self, layout=QHBoxLayout())
        self.__use_buffer__ = CheckBoxWidget(self.__use_parameters__,
                                             i18n_def='Use buffer',
                                             checked=True)
        self.__use_identity_line__ = CheckBoxWidget(self.__use_parameters__,
                                             i18n_def='Use identity line',
                                             checked=True)

    @property
    def use_buffer(self):
        return self.__use_buffer__.isChecked()

    @property
    def use_identity_line(self):
        return self.__use_identity_line__.isChecked()

    @property
    def size(self):
        return self.__window_size__.size

    def changeUnit(self, _unit):
        self.__window_size__.setUnit(_unit)
        self.__window_size__.setValueInUnit(_unit)

    @property
    def unit(self):
        return self.__unitsWidget__.getUnit()


class __DataWindowSizeWidget__(CompositeWidget):
    """
    widget used to change data window size
    """
    def __init__(self, parent, data_accessor):
        super(__DataWindowSizeWidget__, self).__init__(parent,
                                            layout=QVBoxLayout())

        self.data_accessor = data_accessor

        info_group = CompositeWidget(self, layout=QHBoxLayout())
        LabelWidget(info_group, i18n_def='Data window size:')
        self.__size_value__ = LabelWidget(info_group, i18n_def='<value>')
        self.__unit_value__ = LabelWidget(info_group, i18n_def='')

        self.__size_slider__ = SliderWidget(self, orientation=Qt.Horizontal,
                        sizePolicy=QSizePolicy(QSizePolicy.MinimumExpanding,
                                               QSizePolicy.Fixed),
                        value_changed_handler=self.__value_changed__)
        self.__size_slider__.setTickPosition(QSlider.TicksBelow)
        self.setValueInUnit(self.data_accessor.signal_x_unit)
        self.setUnit(self.data_accessor.signal_x_unit)

    def __value_changed__(self, _value):
        self.__size_value__.setText(str(_value))

    def setValueInUnit(self, _unit):
        signal = self.data_accessor.signal_in_unit(_unit)
        self.__size_slider__.setMaximum(int(pl.amax(signal)))
        self.__size_slider__.setValue(0)
        self.__size_slider__.setTickInterval(self.__size_slider__.maximum() / 10 ) # @IgnorePep8

    def setUnit(self, _unit):
        self.__unit_value__.setText(_unit.name)

    @property
    def size(self):
        return self.__size_slider__.value()


class __MiscellaneousVectorListener__(DataVectorListener):
    """
    data accessor listener used to set up some poincare plot
    and data vector parameters based on values of widgets included
    in MiscellaneousWidget
    """
    def __init__(self, _miscellaneous_widget):
        self.__miscellaneous_widget__ = _miscellaneous_widget

    def prepareParameters(self, data_vector_accessor):
        w = self.__miscellaneous_widget__  # alias

        container = data_vector_accessor.parameters_container
        parameters = container.getParametersObject(
                        PoincarePlotParameters.NAME, PoincarePlotParameters)

        parameters.use_buffer = w.use_buffer
        parameters.use_identity_line = w.use_identity_line

        parameters = container.getParametersObject(
                        DataVectorParameters.NAME, DataVectorParameters)
        unit = w.unit
        if unit == OrderUnit:
            parameters.window_size = w.size
        else:
            #window size has to include window signal unit
            parameters.window_size = str(w.size) + unit.label
        parameters.window_shift = 1  # at this moment it's a constant value
