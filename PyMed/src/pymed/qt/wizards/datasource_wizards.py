'''
Created on 03-11-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.qt_i18n import title_I18N
from pygui.qt.utils.widgets import createComposite
from pygui.qt.utils.widgets import createTableView
from pygui.qt.utils.widgets import createLineEdit
from pygui.qt.utils.widgets import createCheckBox
from pygui.qt.utils.widgets import createLabel
from pygui.qt.utils.widgets import createPushButton
from pygui.qt.utils.widgets import createGroupBox
from pygui.qt.utils.graphics import get_width_of_n_letters


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

    def initializePage(self):
        title_I18N(self, "datasource.page.title", "Datasource chooser")
        #self.setSubTitle('Setup frame specific data')
        pageLayout = QVBoxLayout()
        self.setLayout(pageLayout)
        self.__createDatasourceGroupBox(pageLayout)
        self.__createFilesGroupBox(pageLayout)

    def __createDatasourceGroupBox(self, pageLayout):
        self.datasourceGroupBox = createGroupBox(self,
                                    i18n="datasource.datasource.group.title",
                                    i18n_def="Datasource",
                                    layout=QHBoxLayout())

        self.chooseRootDirButton = createPushButton(self.datasourceGroupBox,
                        i18n="datasource.datasource.choose.root.dir.button",
                        i18n_def="Choose root dir",
                        stretch_after_widget=1)
        self.connect(self.chooseRootDirButton, SIGNAL("clicked()"),
                     self.chooseRootDirAction)

#        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
#        self.rootDirLabel = createLabel(self.datasourceGroupBox,
#                                        i18n="datasource.root.dir.label",
#                                        i18n_def="[Not set]",
#                                        sizePolicy=sizePolicy)

        createLabel(self.datasourceGroupBox,
                    i18n="datasource.file.name.filter.label",
                    i18n_def="Files name filter")

        self.filesExtension = createLineEdit(self.datasourceGroupBox,
                                             #sizePolicy=sizePolicy,
                                             maxLength=9,
                                             width=get_width_of_n_letters(8),
                                             text="*")
        self.recursively = createCheckBox(self.datasourceGroupBox,
                i18n="datasource.search.files.recursively.label",
                i18n_def="Search files recursively")

    def __createFilesGroupBox(self, pageLayout):
        self.filesGroupBox = createGroupBox(self,
                                    i18n="datasource.files.group.title",
                                    i18n_def="Files",
                                    layout=QVBoxLayout(),
                                    enabled=False)

        _dir = createComposite(self.filesGroupBox, layout=QHBoxLayout())

        self.reloadButton = createPushButton(_dir,
                        i18n="datasource.datasource.reload.button",
                        i18n_def="Reload")
        self.connect(self.reloadButton, SIGNAL("clicked()"),
                     self.reloadAction)

        createLabel(_dir,
                     i18n="datasource.root.dir.label",
                     i18n_def="Root dir:")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.rootDirLabel = createLabel(_dir,
                                        i18n="datasource.root.dir.label",
                                        i18n_def="[Not set]",
                                        sizePolicy=sizePolicy)

        self.filesTableView = createTableView(self.filesGroupBox,
                        selectionBehavior=QAbstractItemView.SelectRows,
                        selectionMode=QAbstractItemView.SingleSelection)
        self.filesTableView.setModel(self.model)
        self.filesTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        filesOperations = createComposite(self.filesGroupBox,
                                            layout=QHBoxLayout())

        filePreviewButton = createPushButton(filesOperations,
                            i18n="datasource.file.preview.button",
                            i18n_def="File preview",
                            stretch_after_widget=1)
        self.connect(filePreviewButton, SIGNAL("clicked()"),
                     self.filePreviewAction)

        createLabel(filesOperations,
                     i18n="datasource.re.label",
                     i18n_def="Pattern (a regular expression)")

        self.reEdit = createLineEdit(filesOperations)
        self.checkReButton = createPushButton(filesOperations,
                            i18n="datasource.check.regular.expression.button",
                            i18n_def="Check reg.expr.")

        checkAllButton = createPushButton(filesOperations,
                            i18n="datasource.accept.check.all.button",
                            i18n_def="Check all")
        self.connect(checkAllButton, SIGNAL("clicked()"), self.checkAllAction)

        uncheckAllButton = createPushButton(filesOperations,
                            i18n="datasource.accept.uncheck.all.button",
                            i18n_def="Uncheck all")
        self.connect(uncheckAllButton, SIGNAL("clicked()"),
                     self.uncheckAllAction)

    def chooseRootDirAction(self):
        rootDir = QFileDialog.getExistingDirectory(self,
                                    caption=self.chooseRootDirButton.text())
        if rootDir:
            self.rootDirLabel.setText(rootDir)
            self.reloadAction()

    def checkAllAction(self):
        for idx in range(self.model.rowCount()):
            self.model.item(idx).setCheckState(Qt.Checked)

    def uncheckAllAction(self):
        for idx in range(self.model.rowCount()):
            self.model.item(idx).setCheckState(Qt.Unchecked)

    def filePreviewAction(self):
        pass

    def reloadAction(self):
        _dir = QDir(self.rootDirLabel.text())
        _dir.setFilter(QDir.Filters(QDir.Files))
        if len(self.filesExtension.text()) > 0 \
            and self.filesExtension.text() != "*":
            _dir.setNameFilters(QStringList(self.filesExtension.text()))
        infoList = _dir.entryInfoList()
        self.model.removeRows(0, self.model.rowCount())
        for infoFile in infoList:
            if not (infoFile.isExecutable() or infoFile.size() == 0):
                filename = QStandardItem(infoFile.fileName())
                filename.setCheckState(Qt.Checked)
                filename.setCheckable(True)
                size = QStandardItem(str(infoFile.size()))
                path = QStandardItem(infoFile.path())
                self.model.appendRow((filename, size, path))
        if self.model.rowCount() == 0:
            QMessageBox.critical(self, "Information",
                      "No files in the directory " + _dir.path())
        else:
            self.filesTableView.resizeColumnsToContents()
            self.filesTableView.scrollToTop()
            self.filesGroupBox.setEnabled(True)


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
