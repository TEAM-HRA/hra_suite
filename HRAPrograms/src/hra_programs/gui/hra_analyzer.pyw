'''
Created on 27-09-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    import sys
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_gui.qt.utils.windows import ApplicationMainWindow
    from hra_gui.qt.widgets.application_widget import ApplicationWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)

__version__ = "1.0.0"


def main():
    app = ApplicationWidget(sys.argv)
    app.setOrganizationName("Med")
    app.setOrganizationDomain("med")
    app.setApplicationName("Medical app")
    app.setWindowIcon(QIcon(":/icon.png"))
    appWindow = ApplicationMainWindow(window_title="HRA Analyzer")
    appWindow.showMaximized()
    app.exec_()

main()
