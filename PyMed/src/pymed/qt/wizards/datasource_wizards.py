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

    def show(self):
        self.addPage(ChooseDatasourcePage(self))
        self.addPage(ChooseColumnsDataPage(self))
        self.exec_()


class ChooseDatasourcePage(QWizardPage):

    def __init__(self, _parent):
        QWizardPage.__init__(self, parent=_parent)

        self.model = QStandardItemModel()
        labels = [QT_I18N("datasource.files.column.filename", "Filename"),
                  QT_I18N("datasource.files.column.size", "Size"),
                  QT_I18N("datasource.files.column.path", "File path")]
        labels = QStringList(labels)
        self.model.setHorizontalHeaderLabels(labels)
        self.selectedRow = None
        self.rootDir = None

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

        _dir = createComposite(self.filesGroupBox, layout=QHBoxLayout())

        self.chooseRootDirButton = createPushButton(_dir,
                        i18n="datasource.datasource.choose.root.dir.button",
                        i18n_def="Choose root dir")
        self.connect(self.chooseRootDirButton, SIGNAL("clicked()"),
                     self.chooseRootDirAction)

        createLabel(_dir,
                     i18n="datasource.root.dir.label",
                     i18n_def="Root dir:")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.rootDirLabel = createLabel(_dir,
                                        i18n="datasource.root.dir.label",
                                        i18n_def="[Not set]",
                                        sizePolicy=sizePolicy,
                                        stretch_after_widget=1)

        createLabel(_dir,
                    i18n="datasource.file.name.filter.label",
                    i18n_def="Files name filter")

        self.filesExtension = createLineEdit(_dir,
                                             maxLength=9,
                                             width=get_width_of_n_letters(8),
                                             text="*")
        self.connect(self.filesExtension,
                     SIGNAL("textChanged(const QString&)"),
                     self.filesExtensionAction)

        self.recursively = createCheckBox(_dir,
                i18n="datasource.search.files.recursively.label",
                i18n_def="Search files recursively")
        self.connect(self.recursively, SIGNAL("clicked()"),
                     self.recursivelyAction)

        self.filesTableView = createTableView(self.filesGroupBox,
                        selectionBehavior=QAbstractItemView.SelectRows,
                        selectionMode=QAbstractItemView.SingleSelection)
        self.filesTableView.setModel(self.model)
        self.filesTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.connect(self.filesTableView, SIGNAL('clicked(QModelIndex)'),
                     self.onClickedAction)

        filesOperations = createComposite(self.filesGroupBox,
                                            layout=QHBoxLayout())

        self.filePreviewButton = createPushButton(filesOperations,
                            i18n="datasource.file.preview.button",
                            i18n_def="File preview",
                            stretch_after_widget=1)
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

        self.changeEnablemend(False)

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
        self.filePreviewButton.setEnabled(False)

        iteratorFlag = QDirIterator.Subdirectories \
                if self.recursively.checkState() == Qt.Checked \
                else QDirIterator.NoIteratorFlags

        nameFilters = QStringList(self.filesExtension.text()) \
                    if len(self.filesExtension.text()) > 0 \
                        and not self.filesExtension.text() \
                            in ("*", "*.*", "", None) \
                    else QStringList()

        dir_iterator = QDirIterator(self.rootDirLabel.text(),
                                    nameFilters,
                                    QDir.Filters(QDir.Files),
                                    iteratorFlag)
        self.model.removeRows(0, self.model.rowCount())
        while(dir_iterator.next()):
            infoFile = dir_iterator.fileInfo()
            if infoFile.isFile() == True:
                if self.filesExtension.text() in ("*", "*.*", "", None):
                    if infoFile.isExecutable() or \
                        is_text_file(infoFile.filePath()) == False:
                            continue
                filename = QStandardItem(infoFile.fileName())
                filename.setCheckState(Qt.Checked)
                filename.setCheckable(True)
                size = QStandardItem(str(infoFile.size()))
                path = QStandardItem(infoFile.path())
                self.model.appendRow((filename, size, path))
        if self.model.rowCount() > 0:
            self.filesTableView.resizeColumnsToContents()
            self.filesTableView.scrollToTop()

    def onClickedAction(self, idx):
        self.selectedRow = idx
        #row = idx.row()
        #cols = self.model.columnCount()
        self.filePreviewButton.setEnabled(True)

    def recursivelyAction(self):
        self.reload()

    def filesExtensionAction(self, text):
        self.reload()

    def changeEnablemend(self, enabled):
        self.filesExtension.setEnabled(enabled)
        self.recursively.setEnabled(enabled)
        self.filesTableView.setEnabled(enabled)
        self.filePreviewButton.setEnabled(enabled)
        self.checkAllButton.setEnabled(enabled)
        self.uncheckAllButton.setEnabled(enabled)


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
