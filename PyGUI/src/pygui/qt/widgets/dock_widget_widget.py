'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.collections_utils import nvl
    from pycore.misc import Params
    from pygui.qt.utils.signals import DOCK_WIDGET_LOCATION_CHANGED_SIGNAL
    from pygui.qt.widgets.commons import Common
    from pygui.qt.widgets.commons import prepareWidget
    from pygui.qt.widgets.composite_widget import CompositeWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class DockWidgetCommon(QDockWidget, Common):
    def __init__(self, parent, **params):
        super(DockWidgetCommon, self).__init__(
                            nvl(params.get('title', None), ''), parent)
        if params.get('not_add_widget_to_parent_layout', None) == None:
            params['not_add_widget_to_parent_layout'] = True
        prepareWidget(parent=parent, widget=self, **params)
        self.params = Params(**params)
        if self.params.use_scroll_area == None:
            self.params.use_scroll_area = True
        if not self.params.dock_widget_location_changed == None:
            self.connect(self, DOCK_WIDGET_LOCATION_CHANGED_SIGNAL,
                         self.__dock_widget_location_changed__)
        self.setObjectName(self.__class__.__name__)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea |
                             Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        layout = nvl(self.params.layout, QVBoxLayout())
        if hasattr(layout, 'setMargin'):
            layout.setMargin(0)
        self.scrollArea = None
        if self.params.use_scroll_area:
            self.scrollArea = QScrollArea(self)

        self.dockComposite = CompositeWidget(self, layout=layout,
                                        not_add_widget_to_parent_layout=True)

        if self.params.use_scroll_area:
            self.scrollArea.setWidget(self.dockComposite)
            self.scrollArea.setWidgetResizable(True)
            self.setWidget(self.scrollArea)
        else:
            self.setWidget(self.dockComposite)

    def closeEvent(self, event):
        if self.params.not_closable:
            event.ignore()

    def __dock_widget_location_changed__(self, dockWidgetArea):
        if not self.params.dock_widget_location_changed == None:
            self.params.dock_widget_location_changed(dockWidgetArea)
