'''
Created on 13-12-2012

@author: jurek
'''
from os.path import join
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pycore.misc import Params
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.widgets import createLabel
from pygui.qt.utils.widgets import createTabWidget
from pygui.qt.utils.widgets import createWidget
from pygui.qt.utils.widgets import createPlainTextEdit
from pygui.qt.utils.widgets import createPushButton
from pygui.qt.menu.menus import QTMenuBuilder
from pycore.globals import GLOBALS
import sys
from pycore.introspection import get_class_object
from pygui.qt.utils.signals import ADD_TAB_WIDGET_SIGNAL


class MainWindow(QMainWindow):

    def __init__(self, parent=None,
                 create_menus=True,
                 main_workspace_name=GLOBALS.WORKSPACE_NAME,
                 main_widget_name=GLOBALS.TAB_MAIN_NAME,
                 **params):
        super(MainWindow, self).__init__(parent)
        self.params = Params(**params)
        self.setObjectName(GLOBALS.MAIN_WINDOW_NAME)

        self.setWindowTitle(self.params.window_title)

        if create_menus == True:
            menuBuilder = QTMenuBuilder(self)
            menuBuilder.createMenus()

            if GLOBALS.START_MENU_ID:
                if menuBuilder.invokeMenuItem(GLOBALS.START_MENU_ID):
                    sys.exit(0)

        self.mainTabWidget = None
        if main_workspace_name:
            self.mainTabWidget = createTabWidget(self,
                            object_name=main_workspace_name,
                            not_add_widget_to_parent_layout=True)
            if main_widget_name:
                self.mainWidget = createWidget(self.mainTabWidget)
                self.mainTabWidget.addTab(self.mainWidget, main_widget_name)
                self.setCentralWidget(self.mainTabWidget)

        self.connect(self, ADD_TAB_WIDGET_SIGNAL, self.addTabWidget)

    def addTabWidget(self, _tab_widget_name, _tab_widget_classname, _model):
        if self.mainTabWidget == None:
            InformationWindow(message='Main tab widget not created!')
            return

        _class_object = get_class_object(_tab_widget_classname)
        tabWidget = _class_object(parent=self.mainTabWidget, model=_model)
        self.mainTabWidget.addTab(tabWidget, _tab_widget_name)


def InformationWindow(parent=None, **params):
    (title, information) = __message__(parent=None, **params)
    QMessageBox.information(parent, title, information)


def ErrorWindow(parent=None, **params):
    (title, error) = __message__(parent=None, title_default='Error', **params)
    QMessageBox.information(parent, title, error, QMessageBox.Critical)


def __message__(parent=None, **params):
    local_params = Params(**params)
    if local_params.title_id == None and local_params.title_default == None:
        title = "Information"
    else:
        title = QT_I18N(local_params.title_id,
                        _default=local_params.title_default,
                        **params)
    message = QT_I18N(local_params.message_id,
                          _default=local_params.message,
                          **params)
    return (title, message)


def showFilePreviewDialog(filepath, parent=None):
    if filepath == None:
        InformationWindow(message="No files selected !")
    else:
        dialog = FilePreviewDialog(filepath, parent)
        dialog.exec_()


class FilePreviewDialog(QDialog):

    def __init__(self, filepath, parent=None):
        super(FilePreviewDialog, self).__init__(parent)
        fileparts = [str(part) for part in filepath] \
                    if hasattr(filepath, '__iter__') else [str(filepath)]
        filename = join(*fileparts)
        self.setWindowTitle('Preview of ' + filename)
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setLayout(QVBoxLayout())
        self.lineNumberLabel = createLabel(self)
        self.preview = createPlainTextEdit(self, readonly=True)

        closeButton = createPushButton(self,
                            i18n="close",
                            i18n_def="Close")
        self.connect(closeButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        file_ = QFile(filename)
        if file_.open(QFile.ReadOnly):
            self.preview.insertPlainText(QString(file_.readAll()))
            self.preview.moveCursor(QTextCursor.Start)
            self.lineNumberLabel.setText('Lines # '
                        + str(self.preview.document().lineCount()))
            file_.close()
