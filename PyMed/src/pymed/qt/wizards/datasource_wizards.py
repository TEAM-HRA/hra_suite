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
from pygui.qt.utils.widgets import createSlider
from pygui.qt.utils.widgets import createTextEdit
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

    def initializePage(self):
        title_I18N(self, "datasource.page.title", "Datasource chooser")
        #self.setSubTitle('Setup frame specific data')
        pageLayout = QVBoxLayout()
        self.setLayout(pageLayout)
        self.__createDatasourceGroupBox(pageLayout)
        self.__createFilesGroupBox(pageLayout)
        self.__createPreviewGroupBox(pageLayout)

    def __createDatasourceGroupBox(self, pageLayout):
        datasourceGroupBox = createGroupBox(self,
                                    i18n="datasource.datasource.group.title",
                                    i18n_def="Datasource",
                                    layout=QVBoxLayout())

        directoryConstraint = createGroupBox(datasourceGroupBox,
                                i18n="datasource.directory.constraint.title",
                                i18n_def="Directory constraint",
                                layout=QHBoxLayout())
        self.chooseRootDir = createPushButton(directoryConstraint,
                        i18n="datasource.datasource.choose.root.dir.button",
                        i18n_def="Choose root dir")

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.rootDirLabel = createLabel(directoryConstraint,
                                        i18n="datasource.root.dir.label",
                                        i18n_def="[Not set]",
                                        sizePolicy=sizePolicy)

        filesConstraint = createGroupBox(datasourceGroupBox,
                                    i18n="datasource.files.constraint.title",
                                    i18n_def="Files constraint",
                                    layout=QHBoxLayout())

        createLabel(filesConstraint,
            i18n="datasource.files.extension.label",
            i18n_def="Files extension")

        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.filesExtension = createLineEdit(filesConstraint,
                                             sizePolicy=sizePolicy,
                                             maxLength=5,
                                             width=get_width_of_n_letters(6)
                                             )

        self.recursively = createCheckBox(filesConstraint,
                i18n="datasource.search.files.recursively.label",
                i18n_def="Search files recursively")

        self.acceptButton = createPushButton(datasourceGroupBox,
                                  i18n="datasource.accept.button.label",
                                  i18n_def="Accept datasource",
                                  alignment=Qt.AlignCenter)

    def __createFilesGroupBox(self, pageLayout):
        filesGroupBox = createGroupBox(self,
                                    i18n="datasource.files.group.title",
                                    i18n_def="Files",
                                    layout=QVBoxLayout())
        self.filesTableView = createTableView(filesGroupBox)
        pattern_and_apply = createComposite(filesGroupBox,
                                              layout=QHBoxLayout())
        createLabel(pattern_and_apply,
                     i18n="datasource.re.label",
                     i18n_def="Pattern (a regular expression)")
        self.reEdit = createLineEdit(pattern_and_apply)
        self.reApply = createPushButton(pattern_and_apply,
                                i18n="datasource.re.apply.button.label",
                                i18n_def="Apply")

    def __createPreviewGroupBox(self, pageLayout):
        filePreviewGroupBox = createGroupBox(self,
                                    i18n="datasource.file.preview.group.title",
                                    i18n_def="File preview",
                                    layout=QVBoxLayout())
        previewParameters = createComposite(filePreviewGroupBox,
                                              layout=QHBoxLayout())

        self.showPreview = createCheckBox(previewParameters,
                                i18n="datasource.show.preview.label",
                                i18n_def="Show preview")

        sladerComposite = createComposite(previewParameters,
                                            layout=QVBoxLayout())
        createLabel(sladerComposite,
                      i18n="datasource.number.of.rows.label",
                      i18n_def="Number of rows")
        self.slider = createSlider(sladerComposite,
                                     orientation=Qt.Horizontal)

        self.reload = createPushButton(previewParameters,
                                i18n="datasource.reload.button.label",
                                i18n_def="Reload")

        self.preview = createTextEdit(filePreviewGroupBox)


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
