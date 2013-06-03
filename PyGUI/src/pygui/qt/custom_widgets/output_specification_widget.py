'''
Created on 19 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import get_or_put
    from pycore.misc import Params
    from pycore.misc import Separator
    from pymath.model.data_vector_listener import DataVectorListener
    from pymath.model.file_data_parameters import FileDataParameters
    from pymath.model.file_data_parameters import DEFAULT_OUTPUT_PRECISION
    from pygui.qt.utils.settings import TemporarySettingsHandler
    from pygui.qt.utils.settings import Setter
    from pygui.qt.widgets.group_box_widget import GroupBoxWidget
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
    from pygui.qt.custom_widgets.decimal_precision_widget import DecimalPrecisionWidget # @IgnorePep8
    from pygui.qt.custom_widgets.separator_widget import SeparatorWidget # @IgnorePep8
    from pygui.qt.custom_widgets.dir_widget import DirWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class OutputSpecificationWidget(GroupBoxWidget, TemporarySettingsHandler):
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

        self.loadTemporarySettings()

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

    def saveTemporarySettings(self):
        """
        this method is called automatically when the widget is hiding
        as a part of TemporarySettingsHandler class's interface
        """
        self.saveTemporarySettingsHandler(self.__getSetters__(), _no_conv=True)

    def loadTemporarySettings(self):
        self.loadTemporarySettingsHandler(
            self.__getSetters__(conv=True, conv_2level=True, handlers=True))

    def __getSetters__(self, conv=False, conv_2level=False, handlers=False):
        return [
            Setter(output_dir=self.__output_dir__.directory,
                   _conv=QVariant.toString if conv else None,
                   _handlers=[self.__output_dir__.setDirectory] \
                            if handlers else None),
            Setter(separator=self.__separator__.getSeparatorSign(),
                   _conv=QVariant.toString if conv else None,
                   _conv_2level=str if conv_2level else None,
                   _handlers=[self.__separator__.setSeparator] \
                            if handlers else None),
            Setter(precision=self.__precision__.precision,
                   _conv=QVariant.toInt if conv else None,
                   _handlers=[self.__precision__.setPrecision] \
                            if handlers else None),
            Setter(scale=self.__precision__.scale,
                   _conv=QVariant.toInt if conv else None,
                   _handlers=[self.__precision__.setScale] \
                            if handlers else None),
            Setter(override_existing=self.__override_existing__.isChecked(),
                   _conv=QVariant.toBool if conv else None,
                   _handlers=[self.__override_existing__.setChecked] \
                            if handlers else None),
            ]


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
