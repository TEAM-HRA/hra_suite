'''
Created on 03-11-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    import os
    import sys
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_core.io_utils import is_text_file
    from hra_gui.qt.utils.qt_i18n import title_I18N
    from hra_gui.qt.utils.settings import SettingsFactory
    from hra_gui.qt.utils.settings import Setter
    from hra_gui.qt.utils.graphics import get_width_of_n_letters
    from hra_gui.qt.utils.signals import WIZARD_COMPLETE_CHANGED_SIGNAL
    from hra_gui.qt.utils.windows import showFilesPreviewDialog
    from hra_gui.qt.custom_widgets.modelviews import FilesTableView
    from hra_gui.qt.custom_widgets.progress_bar import ProgressDialogManager
    from hra_gui.qt.widgets.commons import ENABLED_SIGNAL_NAME
    from hra_gui.qt.widgets.label_widget import LabelWidget
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.check_box_widget import CheckBoxWidget
    from hra_gui.qt.widgets.line_edit_widget import LineEditWidget
    from hra_gui.qt.widgets.group_box_widget import GroupBoxWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ChooseDatasourcePage(QWizardPage):

    def __init__(self, _parent):
        QWizardPage.__init__(self, parent=_parent)

    def initializePage(self):
        title_I18N(self, "datasource.page.title", "Datasource chooser")
        #self.setSubTitle('Setup frame specific data')
        pageLayout = QVBoxLayout()
        self.setLayout(pageLayout)
        self.__createFilesGroupBox(pageLayout)

        #to force call of isComplete(self) method by the Wizard framework
        #which causes state next button to be updated
        self.emit(WIZARD_COMPLETE_CHANGED_SIGNAL)
        self.rootDir = None

    def __createFilesGroupBox(self, pageLayout):
        self.filesGroupBox = GroupBoxWidget(self,
                                    i18n="datasource.files.group.title",
                                    i18n_def="Files",
                                    layout=QVBoxLayout())

        self.__createFileConstraintsComposite__(self.filesGroupBox)

        self.__createReloadButton__(self.filesGroupBox)

        self.__createTableView__(self.filesGroupBox)

        self.__createFilesOperationsComposite__(self.filesGroupBox)

        self.changeEnablemend(False)
        self.chooseRootDirButton.setEnabled(True)

    def __createFileConstraintsComposite__(self, parent):
        fileConstraintsComposite = CompositeWidget(parent,
                                                   layout=QHBoxLayout())

        self.chooseRootDirButton = PushButtonWidget(fileConstraintsComposite,
                        i18n="datasource.datasource.choose.root.dir.button",
                        i18n_def="Choose root dir",
                        clicked_handler=self.chooseRootDirAction)

        LabelWidget(fileConstraintsComposite,
                     i18n="datasource.root.dir.label",
                     i18n_def="Root dir:")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.rootDirLabel = LabelWidget(fileConstraintsComposite,
                                        i18n="datasource.root.dir.label",
                                        i18n_def="[Not set]",
                                        sizePolicy=sizePolicy,
                                        stretch_after_widget=1)

        LabelWidget(fileConstraintsComposite,
                    i18n="datasource.file.name.filter.label",
                    i18n_def="Files name filter")

        self.filesExtension = LineEditWidget(fileConstraintsComposite,
                        maxLength=15,
                        width=get_width_of_n_letters(14),
                        text="*",
                        enabled_precheck_handler=self.enabledPrecheckHandler)

        self.recursively = CheckBoxWidget(fileConstraintsComposite,
                        i18n="datasource.search.files.recursively.label",
                        i18n_def="Search files recursively",
                        clicked_handler=self.reload,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

        self.onlyKnownTypes = CheckBoxWidget(fileConstraintsComposite,
                        i18n="datasource.only.known.types.checkbox",
                        i18n_def="Only known types",
                        checked=True,
                        clicked_handler=self.reload,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

    def __createReloadButton__(self, parent):
        self.reloadButton = PushButtonWidget(parent,
                        i18n="datasource.reload.button",
                        i18n_def="Reload",
                        clicked_handler=self.reload,
                        alignment=Qt.AlignRight,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

    def __createTableView__(self, parent):
        self.filesTableView = FilesTableView(parent,
                        model=QStandardItemModel(self),
                        onClickedAction=self.onClickedAction,
                        wizardButtons=(QWizard.NextButton,),
                        wizard_handler=self.wizard,
                        sorting=True,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

    def __createFilesOperationsComposite__(self, parent):
        filesOperations = CompositeWidget(parent,
                                            layout=QHBoxLayout())

        self.filePreviewButton = PushButtonWidget(filesOperations,
                        i18n="datasource.file.preview.button",
                        i18n_def="File preview",
                        stretch_after_widget=1,
                        clicked_handler=self.filePreviewAction,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

        self.selectAllButton = PushButtonWidget(filesOperations,
                        i18n="datasource.accept.select.all.button",
                        i18n_def="Select all",
                        enabled=False,
                        clicked_handler=self.__select_all_handler__,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

        self.unselectAllButton = PushButtonWidget(filesOperations,
                        i18n="datasource.accept.unselect.all.button",
                        i18n_def="Unselect all",
                        enabled=False,
                        clicked_handler=self.__unselect_all_handler__,
                        enabled_precheck_handler=self.enabledPrecheckHandler)

    def chooseRootDirAction(self):
        SettingsFactory.loadSettings(self, Setter(rootDir=None))

        rootDir = QFileDialog.getExistingDirectory(self,
                                    caption=self.chooseRootDirButton.text(),
                                    directory=self.rootDir)
        if rootDir:
            self.rootDir = rootDir + os.path.sep
            SettingsFactory.saveSettings(self, Setter(rootDir=self.rootDir))
            self.rootDirLabel.setText(self.rootDir)
            self.reload()

    def __select_all_handler__(self):
        self.__change_selection__(True)

    def __unselect_all_handler__(self):
        self.__change_selection__(False)

    def __change_selection__(self, _select):
        self.changeEnablemend(False)
        count = self.filesTableView.getRowCount()
        progressManager = ProgressDialogManager(self,
                label_text=("Selecting..." if _select else "Unselecting..."),
                max_value=count)
        with progressManager as progress:
            for idx in range(count):
                if (progress.wasCanceled()):
                    break
                progress.increaseCounter()
                if _select:
                    self.filesTableView.setCheckedRowState(idx, Qt.Checked)
                else:
                    self.filesTableView.setCheckedRowState(idx, Qt.Unchecked)
        self.filesTableView.changeCompleteState()
        self.changeEnablemend(True)

    def filePreviewAction(self):
        showFilesPreviewDialog(
                    self.filesTableView.getSelectedPathAndFilename())

    def reload(self):
        self.changeEnablemend(True)
        if self.rootDirLabel.text():

            self.filesTableView.clear()
            self.changeEnablemend(False)

            iteratorFlag = QDirIterator.Subdirectories \
                            if self.recursively.isChecked() \
                            else QDirIterator.NoIteratorFlags
            nameFilters = QStringList(
                    self.filesExtension.text()) \
                    if len(self.filesExtension.text()) > 0 \
                            and not self.filesExtension.text() \
                                in ("*", "*.*", "", None) \
                    else QStringList()
            self.iterator = QDirIterator(
                                self.rootDirLabel.text(),
                                nameFilters,
                                QDir.Filters(QDir.Files),
                                iteratorFlag)

            with ProgressDialogManager(self) as progress:
                while(self.iterator.next()):
                    if (progress.wasCanceled()):
                        break
                    fileInfo = self.iterator.fileInfo()
                    if fileInfo.size() == 0 or fileInfo.isFile() == False:
                        continue
                    if self.filesExtension.text() in ("*", "*.*", "", None):
                        if (sys.platform == 'win32' \
                            and fileInfo.isExecutable() == True) \
                            or is_text_file(fileInfo.filePath(),
                                    self.onlyKnownTypes.checkState()) == False:
                            continue
                    progress.increaseCounter()

                    checkable = QStandardItem("")
                    checkable.setCheckable(True)
                    filename = QStandardItem(fileInfo.fileName())
                    progress.setLabelText(fileInfo.fileName())
                    size = QStandardItem(str(fileInfo.size()))
                    path = QStandardItem(fileInfo.path())
                    self.filesTableView.addRow((checkable, filename, size, path)) # @IgnorePep8

            self.filesTableView.resizeColumnsToContents()
            self.filesExtension.setFocus()
            self.changeEnablemend(True)

    def onClickedAction(self, idx):
        self.filePreviewButton.setEnabled(True)
        self.filesTableView.onClickedAction(idx)

    def isComplete(self):
        """
        method used by QWizard to check if next/previous buttons have to
        be disabled/enabled (when False/True is returned)
        """
        return self.filesTableView.isCompletedCount()

    def changeEnablemend(self, enabled):
        self.emit(SIGNAL(ENABLED_SIGNAL_NAME), enabled)
        self.chooseRootDirButton.setEnabled(enabled)

    def enabledPrecheckHandler(self, widget):
        """
        only interested widgets return bool value others none value
        """
        if widget in (self.selectAllButton, self.unselectAllButton):
            return self.filesTableView.count() > 0
        elif widget == self.filePreviewButton:
            return self.filesTableView.getSelectedRowCount() > 0

    def getDatasourceModel(self):
        return self.filesTableView.getModel()
