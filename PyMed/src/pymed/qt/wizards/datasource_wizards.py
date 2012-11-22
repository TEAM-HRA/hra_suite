'''
Created on 03-11-2012

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.context import Context
from pycommon.i18n import I18N


class DatasourceWizard(QWizard):

    @staticmethod
    def show_wizard():
        parent = Context(DatasourceWizard.show_wizard).load().parent
        return DatasourceWizard(parent).show()

    def __init__(self, _parent):
        QWizard.__init__(self, _parent)
        self.setWindowTitle(QString(I18N("datasource.import.title",
                                         _default="Datasource import")))

    def show(self):
        self.addPage(ChooseDatasourcePage(self))
        self.addPage(ChooseColumnsDataPage(self))
        self.exec_()


class ChooseDatasourcePage(QWizardPage):

    def __init__(self, _parent):
        QWizardPage.__init__(self, parent=_parent)

    def initializePage(self):
        self.setTitle('Frames')
        self.setSubTitle('Setup frame specific data')
        chooseFileLabel = QLabel("Choose file name:")
        layout = QGridLayout()
        layout.addWidget(chooseFileLabel, 0, 0)
        self.setLayout(layout)


class ChooseColumnsDataPage(QWizardPage):

    def __init__(self, _parent):
        QWizardPage.__init__(self, parent=_parent)

    def initializePage(self):
        self.setTitle('Choose column data')
        self.setSubTitle('Choose column specific data')
        chooseFileLabel = QLabel("Specific data")
        layout = QGridLayout()
        layout.addWidget(chooseFileLabel, 0, 0)
        self.setLayout(layout)
