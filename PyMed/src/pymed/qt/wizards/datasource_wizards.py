'''
Created on 03-11-2012

@author: jurek
'''
from os.path import join
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.qt_i18n import title_I18N
from pygui.qt.utils.widgets import createComposite
from pygui.qt.utils.widgets import ProgressBarManager
from pygui.qt.utils.widgets import createPlainTextEdit
from pygui.qt.utils.widgets import createTableView
from pygui.qt.utils.widgets import createLineEdit
from pygui.qt.utils.widgets import createCheckBox
from pygui.qt.utils.widgets import createLabel
from pygui.qt.utils.widgets import createPushButton
from pygui.qt.utils.widgets import createGroupBox
from pygui.qt.utils.graphics import get_width_of_n_letters
from pycore.io_utils import is_text_file


class DatasourceWizard(QWizard):

    @staticmethod
    def show_wizard(dargs):
        parent = dargs.get('parent', None)
        return DatasourceWizard(parent).show()

    def __init__(self, _parent):
        QWizard.__init__(self, _parent)
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setWindowTitle(QT_I18N("datasource.import.title",
                                    _default="Datasource import"))
        self.datasourcePage = None

    def show(self):
        self.datasourcePage = ChooseDatasourcePage(self)
        self.addPage(self.datasourcePage)
        self.addPage(ChooseColumnsDataPage(self))
        self.exec_()

    def closeEvent(self, event):
        self.datasourcePage.close()


class ChooseDatasourcePage(QWizardPage):

    def __init__(self, _parent):
        QWizardPage.__init__(self, parent=_parent)

        #variable used in a method changeCompleteState()
        #where is an explanation
        self.__completed_count__ = 0

        self.model = QStandardItemModel()
        labels = [QT_I18N("datasource.files.column.filename", "Filename"),
                  QT_I18N("datasource.files.column.size", "Size"),
                  QT_I18N("datasource.files.column.path", "File path")]
        labels = QStringList(labels)
        self.model.setHorizontalHeaderLabels(labels)
        self.selectedRow = None
        self.rootDir = None

    def closeEvent(self, event):
        if self.progressBarManager:
            self.progressBarManager.close()

    def hideEvent(self, event):
        if self.progressBarManager:
            self.progressBarManager.stop()

    def initializePage(self):
        title_I18N(self, "datasource.page.title", "Datasource chooser")
        #self.setSubTitle('Setup frame specific data')
        pageLayout = QVBoxLayout()
        self.setLayout(pageLayout)
        self.__createFilesGroupBox(pageLayout)

    def __createFilesGroupBox(self, pageLayout):
        self.filesGroupBox = createGroupBox(self,
                                    i18n="datasource.files.group.title",
                                    i18n_def="Files",
                                    layout=QVBoxLayout())

        self.__createFileConstraintsComposite__(self.filesGroupBox)

        self.__createReloadButton__(self.filesGroupBox)

        self.__createTableView__(self.filesGroupBox)

        self.__createProgressBarComposite__(self.filesGroupBox)

        self.__createFilesOperationsComposite__(self.filesGroupBox)

        self.changeEnablemend(False)

    def __createFileConstraintsComposite__(self, parent):
        fileConstraintsComposite = createComposite(parent,
                                                   layout=QHBoxLayout())

        self.chooseRootDirButton = createPushButton(fileConstraintsComposite,
                        i18n="datasource.datasource.choose.root.dir.button",
                        i18n_def="Choose root dir")
        self.connect(self.chooseRootDirButton, SIGNAL("clicked()"),
                     self.chooseRootDirAction)

        createLabel(fileConstraintsComposite,
                     i18n="datasource.root.dir.label",
                     i18n_def="Root dir:")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.rootDirLabel = createLabel(fileConstraintsComposite,
                                        i18n="datasource.root.dir.label",
                                        i18n_def="[Not set]",
                                        sizePolicy=sizePolicy,
                                        stretch_after_widget=1)

        createLabel(fileConstraintsComposite,
                    i18n="datasource.file.name.filter.label",
                    i18n_def="Files name filter")

        self.filesExtension = createLineEdit(fileConstraintsComposite,
                                             maxLength=15,
                                             width=get_width_of_n_letters(14),
                                             text="*")
        self.connect(self.filesExtension,
                     SIGNAL("textChanged(const QString&)"),
                     self.reload)

        self.recursively = createCheckBox(fileConstraintsComposite,
                i18n="datasource.search.files.recursively.label",
                i18n_def="Search files recursively")
        self.connect(self.recursively, SIGNAL("clicked()"),
                     self.reload)

        self.onlyKnownTypes = createCheckBox(fileConstraintsComposite,
                i18n="datasource.only.known.types.checkbox",
                i18n_def="Only known types",
                checked=True)
        self.connect(self.onlyKnownTypes, SIGNAL("clicked()"),
                     self.reload)

    def __createReloadButton__(self, parent):
        self.reloadButton = createPushButton(parent,
                                            i18n="datasource.reload.button",
                                            i18n_def="Reload")
        self.connect(self.reloadButton, SIGNAL("clicked()"),
                     self.reload)

    def __createTableView__(self, parent):
        self.filesTableView = createTableView(parent,
                        selectionBehavior=QAbstractItemView.SelectRows,
                        selectionMode=QAbstractItemView.SingleSelection)
        self.filesTableView.setModel(self.model)
        self.filesTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.connect(self.filesTableView, SIGNAL('clicked(QModelIndex)'),
                     self.onClickedAction)

    def __createProgressBarComposite__(self, parent):
        self.progressBarManager = ProgressBarManager(parent, hidden=True)

    def __createFilesOperationsComposite__(self, parent):
        filesOperations = createComposite(parent,
                                            layout=QHBoxLayout())

        self.filePreviewButton = createPushButton(filesOperations,
                            i18n="datasource.file.preview.button",
                            i18n_def="File preview",
                            stretch_after_widget=1,
                            enabled=False)
        self.connect(self.filePreviewButton, SIGNAL("clicked()"),
                     self.filePreviewAction)

        self.checkAllButton = createPushButton(filesOperations,
                            i18n="datasource.accept.check.all.button",
                            i18n_def="Check all")
        self.connect(self.checkAllButton, SIGNAL("clicked()"),
                     self.checkAllAction)

        self.uncheckAllButton = createPushButton(filesOperations,
                            i18n="datasource.accept.uncheck.all.button",
                            i18n_def="Uncheck all")
        self.connect(self.uncheckAllButton, SIGNAL("clicked()"),
                     self.uncheckAllAction)

    def chooseRootDirAction(self):
        rootDir = QFileDialog.getExistingDirectory(self,
                                    caption=self.chooseRootDirButton.text())
        if rootDir:
            self.changeEnablemend(True)
            self.rootDir = rootDir
            self.rootDirLabel.setText(rootDir)
            self.reload()

    def checkAllAction(self):
        self.progressBarManager.start(before=self.beforeCheckProgressBarAction,
                                      progressJob=self.checkProgressBarAction,
                                      after=self.afterCheckProgressBarAction)

    def uncheckAllAction(self):
        self.progressBarManager.start(
                                    before=self.beforeUncheckProgressBarAction,
                                    progressJob=self.uncheckProgressBarAction,
                                    after=self.afterUncheckProgressBarAction)

    def filePreviewAction(self):
        if self.selectedRow == None:
            QMessageBox.information(self, "Information",
                      "No files selected !")
        else:
            model = self.selectedRow.model()
            path = model.item(self.selectedRow.row(), 2)
            filename = model.item(self.selectedRow.row(), 0)
            dialog = FilePreviewDialog(path.text(), filename.text(), self)
            dialog.exec_()

    def reload(self):
        if not self.rootDir == None:
            self.progressBarManager.start(
                    before=self.beforeTableViewProgressAction,
                    progressJob=self.tableViewProgressBarAction,
                    after=self.afterFinishProgressBar)

    def beforeTableViewProgressAction(self):
        self.model.removeRows(0, self.model.rowCount())
        self.changeCompleteState(0)
        self.changeEnablemend(False)
        self.chooseRootDirButton.setEnabled(False)

    def tableViewProgressBarAction(self):
        iteratorFlag = QDirIterator.Subdirectories \
                if self.recursively.checkState() == Qt.Checked \
                else QDirIterator.NoIteratorFlags

        nameFilters = QStringList(self.filesExtension.text()) \
                    if len(self.filesExtension.text()) > 0 \
                        and not self.filesExtension.text() \
                            in ("*", "*.*", "", None) \
                    else QStringList()

        self.dir_iterator = QDirIterator(self.rootDirLabel.text(),
                                    nameFilters,
                                    QDir.Filters(QDir.Files),
                                    iteratorFlag)
        while(self.dir_iterator.next()):
            if self.progressBarManager.isStopped() == True:
                break
            self.progressBarManager.update()
            infoFile = self.dir_iterator.fileInfo()
            if infoFile.isFile() == True and infoFile.size() > 0:
                if self.progressBarManager.isStopped() == True:
                    break
                if self.filesExtension.text() in ("*", "*.*", "", None):
                    if infoFile.isExecutable() == True or \
                        is_text_file(infoFile.filePath(),
                                    self.onlyKnownTypes.checkState()) == False:
                            continue
                filename = QStandardItem(infoFile.fileName())
                filename.setCheckable(True)
                size = QStandardItem(str(infoFile.size()))
                path = QStandardItem(infoFile.path())
                if self.progressBarManager.isStopped() == True:
                    break
                self.model.appendRow((filename, size, path))

    def afterFinishProgressBar(self):
        if self.model.rowCount() > 0:
            self.filesTableView.resizeColumnsToContents()
            self.filesTableView.scrollToTop()
        self.changeEnablemend(True)
        self.chooseRootDirButton.setEnabled(True)
        self.filePreviewButton.setEnabled(False)
        self.filesExtension.setFocus()

    def onClickedAction(self, idx):
        self.selectedRow = idx
        row = idx.row()
        #cols = self.model.columnCount()
        self.filePreviewButton.setEnabled(True)
        checked = self.model.item(row).checkState() == Qt.Checked
        self.changeCompleteState(1, 'add' if checked else 'sub')

    def isComplete(self):
        """
        method used by QWizard to check if next/previous buttons have to
        be disabled/enabled (when False/True is returned)
        """
        return self.__completed_count__ > 0

    def changeCompleteState(self, value, operation='set'):
        """
        method used to emit a signal completeChanged() which is intercepted
        by QWizard to enable/disable next, previous buttons based on value
        returned by isComplete method of a wizard page object
        """
        if operation == 'set':
            self.__completed_count__ = value
        elif operation == 'add':
            self.__completed_count__ = self.__completed_count__ + value
        elif operation == 'sub':
            if self.__completed_count__ - value >= 0:
                self.__completed_count__ = self.__completed_count__ - value
        self.emit(SIGNAL("completeChanged()"))

    def changeEnablemend(self, enabled):
        self.filesExtension.setEnabled(enabled)
        self.recursively.setEnabled(enabled)
        self.filesTableView.setEnabled(enabled)
        self.checkAllButton.setEnabled(enabled)
        self.uncheckAllButton.setEnabled(enabled)
        self.reloadButton.setEnabled(enabled)
        self.onlyKnownTypes.setEnabled(enabled)

    def beforeCheckProgressBarAction(self):
        self.changeEnablemend(False)

    def checkProgressBarAction(self):
        self.__stateProgressBarAction__(Qt.Checked)

    def afterCheckProgressBarAction(self):
        self.changeCompleteState(self.model.rowCount())
        self.changeEnablemend(True)

    def beforeUncheckProgressBarAction(self):
        self.changeEnablemend(False)

    def uncheckProgressBarAction(self):
        self.__stateProgressBarAction__(Qt.Unchecked)

    def afterUncheckProgressBarAction(self):
        self.changeCompleteState(0)
        self.changeEnablemend(True)

    def __stateProgressBarAction__(self, state):
        for idx in range(self.model.rowCount()):
            self.progressBarManager.update()
            if self.progressBarManager.isStopped() == True:
                break
            self.model.item(idx).setCheckState(state)


class ChooseColumnsDataPage(QWizardPage):

    def __init__(self, _parent):
        QWizardPage.__init__(self, parent=_parent)

    def initializePage(self):
        self.setTitle('Choose column data')
        #self.setSubTitle('Choose column specific data')
        chooseFileLabel = QLabel("Specific data")
        layout = QGridLayout()
        layout.addWidget(chooseFileLabel, 0, 0)
        self.setLayout(layout)


class FilePreviewDialog(QDialog):

    def __init__(self, path, filename, parent=None):
        super(FilePreviewDialog, self).__init__(parent)
        filename = QString(join(str(path), str(filename)))
        self.setWindowTitle('Preview of ' + filename)
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setLayout(QVBoxLayout())
        self.lineNumberLabel = createLabel(self)
        self.preview = createPlainTextEdit(self, readonly=True)

        closeButton = createPushButton(self,
                            i18n="close",
                            i18n_def="Close")
        self.connect(closeButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        file_ = QFile(QString(join(str(path), str(filename))))
        if file_.open(QFile.ReadOnly):
            self.preview.insertPlainText(QString(file_.readAll()))
            self.preview.moveCursor(QTextCursor.Start)
            self.lineNumberLabel.setText('Lines # '
                        + str(self.preview.document().lineCount()))
            file_.close()
