'''
Created on 04-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.widgets.dock_widget_widget import DockWidgetWidget
    from pygui.qt.custom_widgets.tabular_data_vector_preview_widget import TabularDataVectorPreviewWidget # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TabularDataVectorPreviewDockWidget(DockWidgetWidget):
    """
    a dock widget to display data vector in a table preview
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
        super(TabularDataVectorPreviewDockWidget, self).__init__(parent,
                        title=params.get('title', 'Data preview'),
                        **params)
        self.data_accessor = self.params.data_accessor  # alias
        self.__createPreviewWidget__(QVBoxLayout())
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

    def __createPreviewWidget__(self, _layout):

        headers = []
        headers.append("Signal")

        data = []
        data.append(self.data_accessor.signal)

        if not self.data_accessor.annotation == None:
            headers.append("Annotation")
            data.append(self.data_accessor.annotation)

        self.__previewWidget__ = TabularDataVectorPreviewWidget(
                                                    self.dockComposite,
                                                    headers=headers,
                                                    data=data)
