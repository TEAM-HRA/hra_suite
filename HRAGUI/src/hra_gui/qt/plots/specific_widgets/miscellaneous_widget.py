'''
Created on 20 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    import pylab as pl
    from hra_core.misc import Params
    from hra_core.units import OrderUnit
    from hra_core.collections_utils import get_or_put
    from hra_math.model.data_vector_listener import DataVectorListener
    from hra_math.model.parameters.data_vector_parameters \
        import DataVectorParameters
    from hra_math.model.parameters.poincare_plot_parameters \
        import PoincarePlotParameters
    from hra_gui.qt.utils.settings import temporarySetterDecorator
    from hra_gui.qt.utils.settings import temporarySettingsDecorator
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.group_box_widget import GroupBoxWidget
    from hra_gui.qt.widgets.check_box_widget import CheckBoxWidget
    from hra_gui.qt.widgets.label_widget import LabelWidget
    from hra_gui.qt.widgets.slider_widget import SliderWidget
    from hra_gui.qt.custom_widgets.units import TimeUnitsWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class MiscellaneousWidget(GroupBoxWidget):
    """
    widget used to set up some specific properties like:
    window size,
    using of internal buffer,
    use line of identity
    """
    @temporarySettingsDecorator()
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

        self.__sample_step__ = __SampleStepWidget__(self,
                                                self.params.data_accessor)

        self.__stepper_size__ = __StepperSizeWidget__(self,
                                                self.params.data_accessor)

    def getUseBuffer(self):
        return self.__use_buffer__.isChecked()

    @temporarySetterDecorator(name='use_buffer',
                              _conv=QVariant.toBool,
                              _getter_handler=getUseBuffer)
    def setUseBuffer(self, use_buffer):
        return self.__use_buffer__.setChecked(use_buffer)

    def getUseIdentityLine(self):
        return self.__use_identity_line__.isChecked()

    @temporarySetterDecorator(name='use_identity_line',
                              _conv=QVariant.toBool,
                              _getter_handler=getUseIdentityLine)
    def setUseIdentityLine(self, use_identity_line):
        self.__use_identity_line__.setChecked(use_identity_line)

    def getWindowSize(self):
        return self.__window_size__.size

    @temporarySetterDecorator(name='window_size',
                              _conv=QVariant.toInt,
                              _getter_handler=getWindowSize)
    def setWindowSize(self, size):
        self.__window_size__.setSize(size)

    def changeUnit(self, _unit):
        self.__window_size__.setUnit(_unit)
        self.__window_size__.setValueInUnit(_unit)

    def getUnit(self):
        return self.__unitsWidget__.getUnit()

    @temporarySetterDecorator(name='window_size_unit',
                              _conv=QVariant.toPyObject,
                              _getter_handler=getUnit)
    def setUnit(self, unit):
        self.changeUnit(unit)
        self.__unitsWidget__.setUnit(unit)

    def getSampleStep(self):
        return self.__sample_step__.step

    @temporarySetterDecorator(name='sample_step',
                              _conv=QVariant.toInt,
                              _getter_handler=getSampleStep)
    def setSampleStep(self, step):
        self.__sample_step__.setStep(step)

    def getStepperSize(self):
        return self.__stepper_size__.size

    @temporarySetterDecorator(name='stepper_size',
                              _conv=QVariant.toInt,
                              _getter_handler=getStepperSize)
    def setStepperSize(self, size):
        self.__stepper_size__.setSize(size)

    def getStepperUnit(self):
        return self.__stepper_size__.unit

    @temporarySetterDecorator(name='stepper_unit',
                              _conv=QVariant.toPyObject,
                              _getter_handler=getStepperUnit,
                              before_name='stepper_size')
    def setStepperUnit(self, unit):
        self.__stepper_size__.changeUnit(unit)


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
        self.__size_slider__.setTickInterval(self.__size_slider__.maximum() / 10)  # @IgnorePep8

    def setUnit(self, _unit):
        self.__unit_value__.setText(_unit.name)

    @property
    def size(self):
        return self.__size_slider__.value()

    def setSize(self, _size):
        self.__size_slider__.setValue(int(_size))


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

        parameters.use_buffer = w.getUseBuffer()
        parameters.use_identity_line = w.getUseIdentityLine()

        parameters = container.getParametersObject(
                        DataVectorParameters.NAME, DataVectorParameters)
        parameters.sample_step = w.getSampleStep()

        if not w.getStepperSize() == None:
            if w.getStepperUnit() == OrderUnit:
                parameters.stepper = str(w.getStepperSize())
            else:
                parameters.stepper = str(w.getStepperSize()) + w.getStepperUnit().label  # @IgnorePep8

        unit = w.getUnit()
        if unit == OrderUnit:
            parameters.window_size = w.getWindowSize()
        else:
            # window size has to include window signal unit
            parameters.window_size = str(w.getWindowSize()) + unit.label
        parameters.window_shift = 1  # at this moment it's a constant value


class __SampleStepWidget__(CompositeWidget):
    """
    widget used to change sample step value
    """
    def __init__(self, parent, data_accessor):
        super(__SampleStepWidget__, self).__init__(parent,
                                            layout=QVBoxLayout())

        self.data_accessor = data_accessor

        info_group = CompositeWidget(self, layout=QHBoxLayout())
        LabelWidget(info_group, i18n_def='Sample step:')
        self.__step_value__ = LabelWidget(info_group, i18n_def='<value>')
        self.__unit_value__ = LabelWidget(info_group, i18n_def='')

        self.__step_slider__ = SliderWidget(self, orientation=Qt.Horizontal,
                        sizePolicy=QSizePolicy(QSizePolicy.MinimumExpanding,
                                               QSizePolicy.Fixed),
                        value_changed_handler=self.__value_changed__)
        self.__step_slider__.setTickPosition(QSlider.TicksBelow)
        self.setValueInSignalUnit()
        self.setUnit()

    def __value_changed__(self, _value):
        self.__step_value__.setText(str(_value))

    def setValueInSignalUnit(self):
        signal = self.data_accessor.signal
        self.__step_slider__.setMaximum(int(pl.amax(signal)))
        self.__step_slider__.setValue(0)
        self.__step_slider__.setTickInterval(self.__step_slider__.maximum() / 10)  # @IgnorePep8

    def setUnit(self):
        self.__unit_value__.setText(
                            self.data_accessor.signal_unit.display_label)

    @property
    def step(self):
        value = self.__step_slider__.value()
        return None if value == 0 else value

    def setStep(self, _step):
        self.__step_slider__.setValue(_step)


class __StepperSizeWidget__(CompositeWidget):
    """
    widget used to change stepper size
    """
    def __init__(self, parent, data_accessor):
        super(__StepperSizeWidget__, self).__init__(parent,
                                            layout=QVBoxLayout())

        self.data_accessor = data_accessor

        info_group = CompositeWidget(self, layout=QHBoxLayout())
        LabelWidget(info_group, i18n_def='Stepper size:')
        self.__size_value__ = LabelWidget(info_group, i18n_def='<value>')
        self.__unit_value__ = LabelWidget(info_group, i18n_def='')

        self.__size_slider__ = SliderWidget(self, orientation=Qt.Horizontal,
                        sizePolicy=QSizePolicy(QSizePolicy.MinimumExpanding,
                                               QSizePolicy.Fixed),
                        value_changed_handler=self.__value_changed__)
        self.__size_slider__.setTickPosition(QSlider.TicksBelow)
        self.setValueInUnit(self.data_accessor.signal_x_unit)
        self.setUnit(self.data_accessor.signal_x_unit)

        self.__unitsWidget__ = TimeUnitsWidget(self, i18n_def='Units',
                        default_unit=self.data_accessor.signal_x_unit,
                        change_unit_handler=self.changeUnit,
                        layout=QHBoxLayout())
        self.__unitsWidget__.addUnit(OrderUnit)

    def __value_changed__(self, _value):
        self.__size_value__.setText(str(_value))

    def setValueInUnit(self, _unit):
        signal = self.data_accessor.signal_in_unit(_unit)
        self.__size_slider__.setMaximum(int(pl.amax(signal)))
        self.__size_slider__.setValue(0)
        self.__size_slider__.setTickInterval(self.__size_slider__.maximum() / 10)  # @IgnorePep8

    def setUnit(self, _unit):
        self.__unit_value__.setText(_unit.name)

    @property
    def size(self):
        value = self.__size_slider__.value()
        return None if value == 0 else value

    def setSize(self, _size):
        self.__size_slider__.setValue(int(_size))

    def changeUnit(self, _unit):
        if not _unit == None:
            self.setValueInUnit(_unit)
            self.setUnit(_unit)
            self.__unitsWidget__.setUnit(_unit)

    @property
    def unit(self):
        return self.__unitsWidget__.getUnit()
