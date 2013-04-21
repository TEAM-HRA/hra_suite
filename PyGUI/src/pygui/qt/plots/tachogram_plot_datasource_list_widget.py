'''
Created on 06-04-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.misc import Params
    from pygui.qt.utils.windows import showFilesPreviewDialog
    from pygui.qt.utils.widgets import WidgetCommon
    from pygui.qt.utils.widgets import ListWidgetCommon
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
    from pygui.qt.utils.widgets import ListWidgetItemCommon
    from pygui.qt.custom_widgets.toolbars import OperationalToolBarWidget
    from pygui.qt.custom_widgets.toolbars import ToolBarManager
    from pygui.qt.custom_widgets.toolbars import CheckUncheckToolBarWidget
    from pygui.qt.custom_widgets.progress_bar import ProgressDialogManager
    from pygui.qt.utils.widgets import maximize_widget
    from pygui.qt.utils.widgets import restore_widget
    from pygui.qt.utils.signals import ENABLEMEND_SIGNAL
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class TachogramPlotDatasourceListWidget(WidgetCommon):
    def __init__(self, parent, model, **params):
        super(TachogramPlotDatasourceListWidget, self).__init__(parent,
                                                    add_widget_to_parent=True,
                                                    layout=QVBoxLayout())
        self.params = Params(**params)
        toolbars = ToolBarManager(self, CheckUncheckToolBarWidget,
                OperationalToolBarWidget,
                toolbar_close_handler=self.params.close_tachogram_plot_handler)
        self.layout().addWidget(toolbars)

        self.__showTachogramsButton__ = PushButtonWidget(self,
                    i18n="poincare.plot.show.tachograms.button",
                    i18n_def="Show tachograms",
                    enabled=False,
                    clicked_handler=self.__showTachogramsHandler__,
                    enabled_precheck_handler=self.__enabledPrecheckHandler__)

        self.__allowTachogramsDuplicationButton__ = CheckBoxWidget(self,
                    i18n="poincare.plot.allow.tachograms.duplications.button",
                    i18n_def="Allow tachograms duplication",
                    enabled=False,
                    enabled_precheck_handler=self.__enabledPrecheckHandler__)

        self.__closeAllTachogramsButton__ = PushButtonWidget(self,
                    i18n="poincare.plot.close.all.tachograms.button",
                    i18n_def="Close all tachograms",
                    enabled=False,
                    clicked_handler=self.__closeTachogramsHandler__)

        self.__datasourceList__ = \
            ListWidgetCommon(self,
                list_item_clicked_handler=self.__datasourceItemClickedHandler__, # @IgnorePep8
                list_item_double_clicked_handler=self.__datasourceDoubleItemClickedHandler__, # @IgnorePep8
                selectionMode=QAbstractItemView.MultiSelection,
                selectionBehavior=QAbstractItemView.SelectRows)
        if len(model) > 0:
            for row in range(len(model)):
                fileSpecification = model[row]
                ListWidgetItemCommon(self.__datasourceList__,
                                     text=fileSpecification.filename,
                                     data=fileSpecification)
        else:
            ListWidgetItemCommon(self.__datasourceList__,
                                 text='model not specified or incorrect type')

        self.__filesPreviewButton__ = PushButtonWidget(self,
                    i18n="poincare.plot.files.preview.button",
                    i18n_def="Files preview",
                    enabled=False,
                    clicked_handler=self.__filesPreviewHandler__,
                    enabled_precheck_handler=self.__enabledPrecheckHandler__)

    def __datasourceItemClickedHandler__(self, listItem):
        self.emit(ENABLEMEND_SIGNAL, listItem.isSelected())

    def __showTachogramsHandler__(self):
        self.__showTachograms__(self.__getFilesSpecifications__(selected=True))

    def __filesPreviewHandler__(self):
        showFilesPreviewDialog(self.__getFilesSpecifications__(selected=True))

    def __datasourceDoubleItemClickedHandler__(self, listItem):
        self.__showTachograms__(self.__getFilesSpecifications__([listItem]))

    def __showTachograms__(self, files_specifications):
        progressManager = ProgressDialogManager(self,
                                        label_text="Create tachograms",
                                        max_value=len(files_specifications))
        firstFocus = True
        checked = self.__allowTachogramsDuplicationButton__.isChecked()
        with progressManager as progress:
            for idx in range(progress.maximum()):
                if (progress.wasCanceled()):
                    break
                progress.increaseCounter()
                tachogram_plot = self.params.add_tachogram_plot_handler(
                                            files_specifications[idx],
                                            checked, firstFocus)
                if firstFocus and tachogram_plot:
                    firstFocus = False

        self.__datasourceList__.clearSelection()

    def __enabledPrecheckHandler__(self, widget):
        """
        only interested widgets return bool value others return none value
        """
        if widget in (self.__showTachogramsButton__,
                      self.__allowTachogramsDuplicationButton__,
                      self.__filesPreviewButton__):
            return len(self.__datasourceList__.selectedIndexes()) > 0

    def __closeTachogramsHandler__(self):
        if self.params.close_tachograms_handler:
            if self.params.close_tachograms_handler():
                self.__closeAllTachogramsButton__.setEnabled(False)
        self.toolbar_uncheck_handler()

    def toolbar_uncheck_handler(self):
        self.__datasourceList__.clearSelection()
        self.emit(ENABLEMEND_SIGNAL, False)

    def toolbar_check_handler(self):
        self.__datasourceList__.selectAll()
        self.emit(ENABLEMEND_SIGNAL, True)

    def toolbar_maximum_handler(self):
        maximize_widget(self)

    def toolbar_restore_handler(self):
        restore_widget(self)

    def enabledCloseAllTachogramsButton(self, enabled):
        self.__closeAllTachogramsButton__.setEnabled(enabled)

    def __getFilesSpecifications__(self, list_items=None, selected=False):
        if selected:  # get files specifications from selected items
            list_items = self.__datasourceList__.selectedItems()
        #acquired from data buffer of list items file specification objects
        return [list_item.getData() for list_item in list_items]
