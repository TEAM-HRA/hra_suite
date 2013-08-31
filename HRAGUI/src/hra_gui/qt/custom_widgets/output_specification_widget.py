'''
Created on 19 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.collections_utils import get_or_put
    from hra_core.misc import Params
    from hra_core.misc import Separator
    from hra_math.model.data_vector_listener import DataVectorListener
    from hra_math.model.file_data_parameters import FileDataParameters
    from hra_math.model.file_data_parameters import DEFAULT_OUTPUT_PRECISION
    from hra_gui.qt.utils.settings import temporarySetterDecorator
    from hra_gui.qt.utils.settings import temporarySettingsDecorator
    from hra_gui.qt.widgets.group_box_widget import GroupBoxWidget
    from hra_gui.qt.widgets.check_box_widget import CheckBoxWidget
    from hra_gui.qt.custom_widgets.decimal_precision_widget import DecimalPrecisionWidget # @IgnorePep8
    from hra_gui.qt.custom_widgets.separator_widget import SeparatorWidget # @IgnorePep8
    from hra_gui.qt.custom_widgets.dir_widget import DirWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class OutputSpecificationWidget(GroupBoxWidget):
    """
    widget used to specify output parameters like:
    output dir,
    output data precision,
    output data separator,
    whether skip existing outcomes
    """
    @temporarySettingsDecorator()
    def __init__(self, parent, **params):
        get_or_put(params, 'layout', QVBoxLayout())
        get_or_put(params, 'i18n_def', 'Output specification')
        super(OutputSpecificationWidget, self).__init__(parent, **params)
        self.params = Params(**params)
        if self.params.data_accessor:
            self.params.data_accessor.addListener(self,
                            __OutputSpecificationDataVectorListener__(self))
        self.__output_dir__ = DirWidget(self)
        precision = self.__get_output_precision__()
        self.__precision__ = DecimalPrecisionWidget(self,
                                                    precision=precision[0],
                                                    scale=precision[1])
        self.__separator__ = SeparatorWidget(self, i18n_def='Output separator',
                no_custom_separator=params.get('no_custom_separator', None),
                default_separator=Separator.WHITE_SPACE)
        self.__override_existing__ = CheckBoxWidget(self,
                                        i18n_def='Override existing outcomes',
                                        checked=False)

    def __get_output_precision__(self):
        """
        return precision defined in FileDataParameters object or a default one
        """
        if self.params.data_accessor:
            container = self.params.data_accessor.parameters_container
            parameters = container.getParametersObject(
                                FileDataParameters.NAME, FileDataParameters)
            return parameters.output_precision
        else:
            return DEFAULT_OUTPUT_PRECISION

    def __getSeparator__(self):
        return self.__separator__.getSeparatorSign()

    @temporarySetterDecorator(name='separator',
                              _conv=QVariant.toString,
                              _conv_2level=str,
                              _getter_handler=__getSeparator__)
    def __setSeparator__(self, separator):
        self.__separator__.setSeparator(separator)

    def __getDirectory__(self):
        return self.__output_dir__.directory

    @temporarySetterDecorator(name='output_dir',
                              _conv=QVariant.toString,
                              _getter_handler=__getDirectory__)
    def __setDirectory__(self, directory):
        self.__output_dir__.setDirectory(directory)

    def __getScale__(self):
        return self.__precision__.scale

    @temporarySetterDecorator(name='scale',
                              _conv=QVariant.toInt,
                              _getter_handler=__getScale__)
    def __setScale__(self, scale):
        self.__precision__.setScale(scale)

    def __getPrecision__(self):
        return self.__precision__.precision

    @temporarySetterDecorator(name='precision',
                              _conv=QVariant.toInt,
                              _getter_handler=__getPrecision__)
    def __setPrecision__(self, precision):
        self.__precision__.setPrecision(precision)

    def __getOverrideExisting__(self):
        return self.__override_existing__.isChecked()

    @temporarySetterDecorator(name='override_existing',
                              _conv=QVariant.toBool,
                              _getter_handler=__getOverrideExisting__)
    def __setOverrideExisting__(self, override_existing):
        self.__override_existing__.setChecked(override_existing)


class __OutputSpecificationDataVectorListener__(DataVectorListener):
    """
    data accessor listener used to set up some file data parameters
    """
    def __init__(self, _output_specification_widget):
        self.__output_specification_widget__ = _output_specification_widget

    def prepareParameters(self, data_vector_accessor):
        container = data_vector_accessor.parameters_container
        parameters = container.getParametersObject(
                                FileDataParameters.NAME, FileDataParameters)
        w = self.__output_specification_widget__  # alias
        parameters.override_existing_outcomes = w.__override_existing__.isChecked()  # @IgnorePep8
        parameters.output_dir = w.__output_dir__.directory
        parameters.output_precision = (w.__precision__.precision, w.__precision__.scale) # @IgnorePep8
        parameters.output_separator = w.__separator__.getSeparatorSign()
