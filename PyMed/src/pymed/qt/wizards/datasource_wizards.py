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
from pygui.qt.utils.widgets import createProgressBar
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
        self.maxProgressBarValue = 1000
        QWizardPage.__init__(self, parent=_parent)

        self.model = QStandardItemModel()
        labels = [QT_I18N("datasource.files.column.filename", "Filename"),
                  QT_I18N("datasource.files.column.size", "Size"),
                  QT_I18N("datasource.files.column.path", "File path")]
        labels = QStringList(labels)
        self.model.setHorizontalHeaderLabels(labels)
        self.selectedRow = None
        self.rootDir = None
        self.tableViewModelThread = FilesTableViewModelThread(self)
        self.tableViewModelThread.setModel(self.model)
        self.connect(self.tableViewModelThread, SIGNAL('taskUpdated'),
                     self.progressBarAction)
        self.connect(self.tableViewModelThread, SIGNAL('taskFinished'),
                     self.progressBarFinishedAction)

    def progressBarAction(self):
        self.progressBar.setValue(0)

    def closeEvent(self, event):
        if not self.tableViewModelThread == None:
            self.tableViewModelThread.close()

    def hideEvent(self, event):
        self.stopTableViewLoaderThread()

    def stopTableViewLoaderThread(self):
        if not self.tableViewModelThread == None:
            self.tableViewModelThread.stop()

    def progressBarFinishedAction(self):
        if self.model.rowCount() > 0:
            self.filesTableView.resizeColumnsToContents()
            self.filesTableView.scrollToTop()
        self.progressBar.reset()
        self.progressBarComposite.hide()
        self.changeEnablemend(True)
        self.chooseRootDirButton.setEnabled(True)
        self.filePreviewButton.setEnabled(False)
        self.filesExtension.setFocus()

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
                     self.reloadAction)

        self.recursively = createCheckBox(fileConstraintsComposite,
                i18n="datasource.search.files.recursively.label",
                i18n_def="Search files recursively")
        self.connect(self.recursively, SIGNAL("clicked()"),
                     self.reloadAction)

        self.onlyKnownTypes = createCheckBox(fileConstraintsComposite,
                i18n="datasource.only.known.types.checkbox",
                i18n_def="Only known types",
                checked=True)
        self.connect(self.onlyKnownTypes, SIGNAL("clicked()"),
                     self.reloadAction)

    def __createReloadButton__(self, parent):
        self.reloadButton = createPushButton(parent,
                                            i18n="datasource.reload.button",
                                            i18n_def="Reload")
        self.connect(self.reloadButton, SIGNAL("clicked()"),
                     self.reloadAction)

    def __createTableView__(self, parent):
        self.filesTableView = createTableView(parent,
                        selectionBehavior=QAbstractItemView.SelectRows,
                        selectionMode=QAbstractItemView.SingleSelection)
        self.filesTableView.setModel(self.model)
        self.filesTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.connect(self.filesTableView, SIGNAL('clicked(QModelIndex)'),
                     self.onClickedAction)

    def __createProgressBarComposite__(self, parent):
        self.progressBarComposite = createComposite(parent,
                                            layout=QHBoxLayout())
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.progressBar = createProgressBar(self.progressBarComposite,
                                             sizePolicy=sizePolicy)
        self.progressBar.setRange(0, 0)
        self.progressBar.setValue(0)
        self.progressBarComposite.hide()

        self.stopProgressBarButton = createPushButton(
                                self.progressBarComposite,
                                i18n="datasource.stop.progress.bar.button",
                                i18n_def="Stop")
        self.connect(self.stopProgressBarButton, SIGNAL("clicked()"),
                     self.stopTableViewLoaderThread)

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
        for idx in range(self.model.rowCount()):
            self.model.item(idx).setCheckState(Qt.Checked)

    def uncheckAllAction(self):
        for idx in range(self.model.rowCount()):
            self.model.item(idx).setCheckState(Qt.Unchecked)

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
        if self.rootDir == None:
            return
        self.model.removeRows(0, self.model.rowCount())

        self.progressBarComposite.show()

        self.tableViewModelThread.setFileExtension(self.filesExtension.text())
        self.tableViewModelThread.setRootDir(self.rootDirLabel.text())
        self.tableViewModelThread.setRecursivelyState(
                                                self.recursively.checkState())
        self.tableViewModelThread.setOnlyKnownTypes(
                                            self.onlyKnownTypes.checkState())

        self.changeEnablemend(False)
        self.chooseRootDirButton.setEnabled(False)
        self.tableViewModelThread.start()

    def onClickedAction(self, idx):
        self.selectedRow = idx
        #row = idx.row()
        #cols = self.model.columnCount()
        self.filePreviewButton.setEnabled(True)

    def reloadAction(self):
        self.reload()

    def changeEnablemend(self, enabled):
        self.filesExtension.setEnabled(enabled)
        self.recursively.setEnabled(enabled)
        self.filesTableView.setEnabled(enabled)
        self.checkAllButton.setEnabled(enabled)
        self.uncheckAllButton.setEnabled(enabled)
        self.reloadButton.setEnabled(enabled)
        self.onlyKnownTypes.setEnabled(enabled)


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


class FilesTableViewModelThread(QThread):
    def __init__(self, parent):
        QThread.__init__(self, parent)
        self.__stop__ = False
        # used when the thread have o be destroyed without
        # any actions about GUI
        self.__close__ = False
        self.__knownTypes__ = True

    def setFileExtension(self, fileExtension):
        self.__fileExtension__ = fileExtension

    def setRecursivelyState(self, state):
        self.__state__ = state

    def setRootDir(self, rootDir):
        self.__rootDir__ = rootDir

    def setModel(self, model):
        self.__model__ = model

    def setOnlyKnownTypes(self, knownTypes):
        self.__knownTypes__ = knownTypes

    def run(self):
        iteratorFlag = QDirIterator.Subdirectories \
                if self.__state__ == Qt.Checked \
                else QDirIterator.NoIteratorFlags

        nameFilters = QStringList(self.__fileExtension__) \
                    if len(self.__fileExtension__) > 0 \
                        and not self.__fileExtension__ \
                            in ("*", "*.*", "", None) \
                    else QStringList()

        dir_iterator = QDirIterator(self.__rootDir__,
                                    nameFilters,
                                    QDir.Filters(QDir.Files),
                                    iteratorFlag)

        while(dir_iterator.next()):
            if self.__stop__ == True:
                break
            self.emit(SIGNAL('taskUpdated'))
            infoFile = dir_iterator.fileInfo()
            if infoFile.isFile() == True and infoFile.size() > 0:
                if self.__stop__ == True:
                    break
                if self.__fileExtension__ in ("*", "*.*", "", None):
                    if infoFile.isExecutable() == True or \
                        is_text_file(infoFile.filePath(),
                                     self.__knownTypes__) == False:
                            continue
                filename = QStandardItem(infoFile.fileName())
                filename.setCheckState(Qt.Checked)
                filename.setCheckable(True)
                size = QStandardItem(str(infoFile.size()))
                path = QStandardItem(infoFile.path())
                if self.__stop__ == True:
                    break
                self.__model__.appendRow((filename, size, path))

        if self.__close__ == False:
            self.emit(SIGNAL('taskFinished'))
        self.__stop__ = False
        self.__close__ = False

    def stop(self):
        self.__stop__ = True

    def close(self):
        self.__stop__ = True
        self.__close__ = True
