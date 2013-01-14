'''
Created on 05-01-2013

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycore.misc import Params
from pygui.qt.utils.widgets import createSplitter
from pygui.qt.utils.widgets import createListWidget
from pygui.qt.utils.widgets import createWidget
from pygui.qt.models.datasources import DatasourceFilesSpecificationModel


class PoincareTabWidget(QWidget):

    def __init__(self, **params):
        self.params = Params(**params)
        super(PoincareTabWidget, self).__init__(self.params.parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.__splitter__ = createSplitter(self, objectName='poincarePlot',
                                           save_state=True)
        self.__createDatasourceComposite__()
        self.__createPlotComposite__()

        #this method's call is very important, it sets up widgets sizes
        #which make up a splitter;
        #it has to be the last operation in the PoincareTabWidget's
        #creation process
        self.__splitter__.updateSizes()

    def closeTab(self):
        """
        this method includes actions to be invoked when a PoincareTabWidget is closing @IgnorePep8
        """
        self.__splitter__.destroySplitter()

    def __createDatasourceComposite__(self):
        self.__datasourceComposite__ = createWidget(self.__splitter__,
                                                    add_widget_to_parent=True)
        self.__datasourceList__ = createListWidget(
                                                self.__datasourceComposite__)
        model = self.params.model
        if model and \
            isinstance(model, DatasourceFilesSpecificationModel):
            for row in range(model.rowCount()):
                QListWidgetItem(model.fileSpecification(row).filename,
                            self.__datasourceList__)
        else:
            QListWidgetItem('model not specified or incorrect type',
                            self.__datasourceList__)
        if self.__splitter__.sizesLoaded() == False:
            idx = self.__splitter__.indexOf(self.__datasourceComposite__)
            self.__splitter__.setStretchFactor(idx, 1)

    def __createPlotComposite__(self):
        self.__plotComposite__ = createWidget(self.__splitter__,
                                              add_widget_to_parent=True)
        if self.__splitter__.sizesLoaded() == False:
            idx = self.__splitter__.indexOf(self.__plotComposite__)
            self.__splitter__.setStretchFactor(idx, 20)
