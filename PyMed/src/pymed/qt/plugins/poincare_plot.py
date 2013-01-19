'''
Created on 05-01-2013

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pycore.misc import Params
from pygui.qt.utils.widgets import createPushButton
from pygui.qt.utils.widgets import WidgetCommon
from pygui.qt.utils.widgets import createListWidget
from pygui.qt.models.datasources import DatasourceFilesSpecificationModel
from pygui.qt.utils.widgets_custom import SplitterWidget
from pygui.qt.utils.widgets_custom import ToolBarManager
from pygui.qt.utils.widgets_custom import CheckUncheckToolBarWidget
from pygui.qt.utils.signals import ENABLEMEND_SIGNAL
from pygui.qt.plots.tachogram_plot import TachogramPlotManager


class PoincarePlotTabWidget(QWidget):

    def __init__(self, **params):
        self.params = Params(**params)
        super(PoincarePlotTabWidget, self).__init__(self.params.parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.__splitter__ = SplitterWidget(self, objectName='poincarePlot',
                                           save_state=True)
        self.__createDatasourceListWidget__()
        self.__createTachogramPlotManager__()

        #this method's call is very important, it sets up widgets sizes which
        #make up a splitter; it has to be the last operation in
        #the PoincarePlotTabWidget's creation process
        self.__splitter__.updateSizes()

    def closeTab(self):
        """
        this method includes actions to be invoked when a PoincarePlotTabWidget is closing @IgnorePep8
        """
        self.__splitter__.destroySplitter()

    def __createDatasourceListWidget__(self):
        self.__datasourceListWidget__ = \
            DatasourceListWidget(self.__splitter__,
                        self.params.model,
                        add_tachogram_plot_handler=self.__addTachogramPlot__)
        if self.__splitter__.sizesLoaded() == False:
            idx = self.__splitter__.indexOf(self.__datasourceListWidget__)
            self.__splitter__.setStretchFactor(idx, 1)

    def __createTachogramPlotManager__(self):
        self.__tachogramsManager__ = TachogramPlotManager(self.__splitter__,
                                                     add_widget_to_parent=True)
        self.__tachogramsManager__.createInitialPlot()
        if self.__splitter__.sizesLoaded() == False:
            idx = self.__splitter__.indexOf(self.__tachogramsManager__)
            self.__splitter__.setStretchFactor(idx, 20)

    def __addTachogramPlot__(self, pathfile):
        self.__tachogramsManager__.addTachogramPlot()


class DatasourceListWidget(WidgetCommon):
    def __init__(self, parent, model, **params):
        super(DatasourceListWidget, self).__init__(parent,
                                                    add_widget_to_parent=True,
                                                    layout=QVBoxLayout())
        self.params = Params(**params)
        toolbars = ToolBarManager(self, CheckUncheckToolBarWidget)
        self.layout().addWidget(toolbars)

        self.__datasourceList__ = \
            createListWidget(self,
                list_item_clicked_handler=self.__datasourceItemClickedHandler__, # @IgnorePep8
                selectionMode=QAbstractItemView.MultiSelection,
                selectionBehavior=QAbstractItemView.SelectRows)
        if model and \
            isinstance(model, DatasourceFilesSpecificationModel):
            for row in range(model.rowCount()):
                QListWidgetItem(model.fileSpecification(row).filename,
                            self.__datasourceList__)
        else:
            QListWidgetItem('model not specified or incorrect type',
                            self.__datasourceList__)
        self.__showTachogramsButton__ = \
            createPushButton(self,
                    i18n="poincare.plot.show.tachograms.button",
                    i18n_def="Show tachograms",
                    enabled=False,
                    clicked_handler=self.__showTachogramsHandler__,
                    enabled_precheck_handler=self.__enabledPrecheckHandler__)

    def __datasourceItemClickedHandler__(self, listItem):
        self.emit(ENABLEMEND_SIGNAL, listItem.isSelected())

    def __showTachogramsHandler__(self):
        if self.params.add_tachogram_plot_handler:
            self.params.add_tachogram_plot_handler(None)

    def __enabledPrecheckHandler__(self, widget):
        """
        only interested widgets return bool value others return none value
        """
        if widget == self.__showTachogramsButton__:
            return len(self.__datasourceList__.selectedIndexes()) > 0

    def toolbar_uncheck_handler(self):
        self.__datasourceList__.clearSelection()
        self.emit(ENABLEMEND_SIGNAL, False)

    def toolbar_check_handler(self):
        self.__datasourceList__.selectAll()
        self.emit(ENABLEMEND_SIGNAL, True)
