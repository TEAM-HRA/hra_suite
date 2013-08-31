'''
Created on 19 kwi 2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_core.collections_utils import get_or_put
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.frame_widget import FrameWidget
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.widgets.label_widget import LabelWidget
    from hra_gui.qt.utils.colors import ColorRGB
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ChooseColorWidget(CompositeWidget):
    """
    widget used to pick up a color
    """
    def __init__(self, parent, **params):

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        get_or_put(params, 'layout', layout)
        super(ChooseColorWidget, self).__init__(parent, **params)

        get_or_put(params, 'title', 'Color changer')
        get_or_put(params, 'default_color', Qt.black)
        self.params = Params(**params)
        LabelWidget(self, i18n_def=self.params.title)

        PushButtonWidget(self, i18n_def="Change color",
                clicked_handler=self.__change_color_handler__)

        self.__color_area__ = __FrameWidget__(self)

        PushButtonWidget(self, i18n_def="Restore default",
                clicked_handler=self.__restore_default_handler__)

        self.setcolor(self.params.default_color)

    def __change_color_handler__(self):
        color = QColorDialog.getColor(self.params.default_color, self)
        if color.isValid():
            self.setcolor(color)

    def __restore_default_handler__(self):
        self.setcolor(QColor(self.params.default_color))

    def getcolor(self):
        return self.__color_area__.palette().color(QPalette.Window)

    def getcolorRGB(self):
        color = self.getcolor()
        return None if color == None else \
                ColorRGB(color.red(), color.green(), color.blue())

    def setcolor(self, color):
        palette = QPalette(QColor(color))
        self.__color_area__.setAutoFillBackground(True)
        self.__color_area__.setPalette(palette)


class __FrameWidget__(FrameWidget):
    """
    a frame to display a color
    """
    def __init__(self, parent, **params):
        super(__FrameWidget__, self).__init__(parent, **params)

    def sizeHint(self):
        return QSize(100, 50)
