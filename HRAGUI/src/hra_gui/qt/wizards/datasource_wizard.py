'''
Created on 03-11-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_gui.qt.utils.qt_i18n import QT_I18N
    from hra_gui.qt.wizards.pages.choose_datasource_page import ChooseDatasourcePage # @IgnorePep8
    from hra_gui.qt.wizards.pages.choose_columns_data_page import ChooseColumnsDataPage # @IgnorePep8
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
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle(QT_I18N("datasource.import.title",
                                    _default="Datasource import"))

    def show(self):
        self.datasourcePage = ChooseDatasourcePage(self)
        id_ = self.addPage(self.datasourcePage)
        self.addPage(ChooseColumnsDataPage(self, id_))
        self.exec_()

    def closeEvent(self, event):
        self.datasourcePage.close()
