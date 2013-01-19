'''
Created on 16-01-2013

@author: jurek
'''
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pycore.misc import Params
from pygui.qt.utils.settings import SettingsFactory
from pygui.qt.utils.settings import Setter
from pygui.qt.utils.widgets import item
from pygui.qt.utils.widgets import WidgetCommon
from pygui.qt.utils.widgets import ToolBarCommon
from pygui.qt.utils.widgets import Common


class SplitterWidget(QSplitter, Common):
    def __init__(self, parent, **params):
        QSplitter.__init__(self, parent)
        item(parent=parent, widget=self, **params)
        self.params = Params(**params)
        self.setHandleWidth(self.handleWidth() * 2)
        if self.params.save_state:
            SettingsFactory.loadSettings(self,
                    Setter(sizes_list=None,
                           _conv=QVariant.toPyObject,
                           _conv_2level=self.conv2level,
                           objectName=self.params.objectName
                           ))

    def destroySplitter(self):
        if self.params.save_state:
            SettingsFactory.saveSettings(self,
                                         Setter(sizes_list=self.sizes(),
                                            _no_conv=True,
                                            objectName=self.params.objectName))

    def conv2level(self, value):
        return None if value == None else [variant.toInt()[0]
                                           for variant in value]

    def sizesLoaded(self):
        return not self.sizes_list == None and len(self.sizes_list) > 0

    def updateSizes(self):
        if self.sizesLoaded():
            self.setSizes(self.sizes_list)


class ToolBarManager(WidgetCommon):
    """
    this class give ability to join toolbars as a one widget
    """
    def __init__(self, parent=None, *toolbar_classes, **params):
        super(ToolBarManager, self).__init__(parent, **params)

        #toolbars cannot set up their own layouts, one have to remove
        #this parameter to avoid it's propagating to toolbars classes,
        #if there is no layout passed for ToolBarManager then default one
        #is created
        layout = params.pop('layout', QHBoxLayout())
        self.setLayout(layout)

        for toolbar_class in toolbar_classes:
            self.layout().addWidget(toolbar_class(self, **params))


class CheckUncheckToolBarWidget(ToolBarCommon):
    def __init__(self, parent=None, **params):
        super(CheckUncheckToolBarWidget, self).__init__(parent,
                                                _check_fields=['checkable'],
                                                 **params)


class OperationalToolBarWidget(ToolBarCommon):
    def __init__(self, parent=None, _button_types=[], **params):
        super(OperationalToolBarWidget, self).__init__(parent,
                                                _check_fields=['operational'],
                                                **params)
