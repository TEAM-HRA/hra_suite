'''
Created on 03-11-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pygui.qt.utils.qt_i18n import QT_I18N
    from pygui.qt.utils.widgets import *  # @UnusedWildImport
    from pygui.qt.wizards.pages.choose_datasource_page import ChooseDatasourcePage # @IgnorePep8
    from pygui.qt.wizards.pages.choose_columns_data_page import ChooseColumnsDataPage # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)


class DatasourceWizard(QWizard):

    @staticmethod
    def show_wizard(dargs):
        parent = dargs.get('parent', None)
        return DatasourceWizard(parent).show()

    def __init__(self, _parent):
        QWizard.__init__(self, _parent)
        self.setOptions(QWizard.NoBackButtonOnStartPage)
        self.setWizardStyle(QWizard.ModernStyle)
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setWindowTitle(QT_I18N("datasource.import.title",
                                    _default="Datasource import"))

    def show(self):
        self.datasourcePage = ChooseDatasourcePage(self)
        id_ = self.addPage(self.datasourcePage)
        self.addPage(ChooseColumnsDataPage(self, id_))
        self.exec_()

    def closeEvent(self, event):
        self.datasourcePage.close()
