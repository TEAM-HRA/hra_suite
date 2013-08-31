'''
Created on 04-04-2013

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_gui.qt.widgets.dock_widget_widget import DockWidgetWidget
    from hra_gui.qt.custom_widgets.files_tracker_widget import FilesTrackerWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class OutcomeFilesTrackerDockWidget(DockWidgetWidget):
    """
    a dock widget to track outcome files
    """
    def __init__(self, parent, **params):
        self.params = Params(**params)
        self.data_accessor = self.params.data_accessor  # alias
        super(OutcomeFilesTrackerDockWidget, self).__init__(parent,
            title=params.get('title', 'Outcome files tracker'),
            **params)

        self.__createFilesTrackerWidget__(QVBoxLayout())

        parent.addDockWidget(Qt.RightDockWidgetArea, self)

    def __createFilesTrackerWidget__(self, layout):
        self.__files_tracker_widget__ = FilesTrackerWidget(self.dockComposite,
                                                           layout=layout)

    def appendFile(self, _filename):
        self.__files_tracker_widget__.appendFile(_filename)
