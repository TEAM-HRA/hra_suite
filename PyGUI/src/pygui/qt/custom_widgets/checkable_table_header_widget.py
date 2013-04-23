'''
Created on 23 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import collections
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pygui.qt.widgets.label_widget import LabelWidget
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)

HeaderColumn = collections.namedtuple('HeaderColumn', ['name', 'label', 'handler']) # @IgnorePep8


class __Handler__():
    """
    auxiliary class handler to give ability to pass HeaderWidget object itself
    """
    def __init__(self, _handler, _widget):
        self.__handler__ = _handler
        self.__widget__ = _widget

    def __call__(self):
        self.__handler__(self.__widget__)


class HeaderWidget(QWidget):
    """
    header widget used in table view to give ability to select check buttons
    in table header
    """
    def __init__(self, _parent, _header_label, _header_elements):
        QWidget.__init__(self, parent=_parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        LabelWidget(self, i18n_def=_header_label)

        self.__buttons__ = {}
        for header_element in _header_elements:
            handler = __Handler__(header_element.handler, self)
            self.__buttons__[header_element.name] = CheckBoxWidget(self,
                                        i18n_def=header_element.label,
                                        clicked_handler=handler)

    def check(self, _type):
        self.__getButton__(_type).setChecked(True)

    def uncheck(self, _type):
        self.__getButton__(_type).setChecked(False)

    def isChecked(self, _type):
        return self.__getButton__(_type).isChecked()

    def enabled(self, _type, _enabled):
        self.__getButton__(_type).setEnabled(_enabled)

    def enabledAll(self, _enabled):
        for name in self.__buttons__:
            self.enabled(name, _enabled)

    def __getButton__(self, _type):
        return self.__buttons__[_type]

    def buttons(self):
        return self.__buttons__
