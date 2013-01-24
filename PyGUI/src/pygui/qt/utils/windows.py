'''
Created on 13-12-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from os.path import join
    import sys
    import re
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.misc import get_max_number_between_signs
    from pygui.qt.utils.qt_i18n import QT_I18N
    from pygui.qt.utils.widgets import LabelCommon
    from pygui.qt.utils.widgets import MainWindowCommon
    from pygui.qt.utils.widgets import WidgetCommon
    from pygui.qt.utils.widgets import PlainTextEditCommon
    from pygui.qt.utils.widgets import PushButtonCommon
    from pygui.qt.custom_widgets.tabwidget import TabWidgetCommon
    from pygui.qt.activities.activities import ActivityDockWidget
    from pygui.qt.menu.menus import QTMenuBuilder
    from pycore.globals import GLOBALS
    from pycore.introspection import get_class_object
    from pygui.qt.utils.signals import ADD_TAB_WIDGET_SIGNAL
    from pycore.collections import any_indexes
    from pycore.collections import or_values
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ApplicationMainWindow(MainWindowCommon):

    def __init__(self, parent=None,
                 create_menus=True,
                 main_workspace_name=GLOBALS.WORKSPACE_NAME,
                 main_widget_name=GLOBALS.TAB_MAIN_NAME,
                 **params):
        super(ApplicationMainWindow, self).__init__(parent)
        self.params = Params(**params)
        self.setObjectName(GLOBALS.MAIN_WINDOW_NAME)

        self.setWindowTitle(self.params.window_title)

        if create_menus == True:
            menuBuilder = QTMenuBuilder(self)
            menuBuilder.createMenus()

            if GLOBALS.START_MENU_ID:
                if menuBuilder.invokeMenuItem(GLOBALS.START_MENU_ID):
                    sys.exit(0)

        self.applicationMainTabWidget = None
        if main_workspace_name:
            self.applicationMainTabWidget = TabWidgetCommon(self,
                            object_name=main_workspace_name,
                            not_add_widget_to_parent_layout=True
                            )
            if main_widget_name:
                self.mainWidget = MainTabItemWindow(
                                            self.applicationMainTabWidget)
                self.applicationMainTabWidget.addTab(self.mainWidget,
                                                     main_widget_name)
                self.setCentralWidget(self.applicationMainTabWidget)

        self.connect(self, ADD_TAB_WIDGET_SIGNAL, self.addTabWidget)

    def addTabWidget(self, _tab_widget_name, _tab_widget_classname, _model,
                     _reuse):
        if self.applicationMainTabWidget == None:
            InformationWindow(message="Main tab widget wasn't created!")
            return

        _class_object = get_class_object(_tab_widget_classname)
        tabWidget = _class_object(parent=self.applicationMainTabWidget,
                                  model=_model)

        #get all tab titles
        titles = [str(self.applicationMainTabWidget.tabText(idx))
                   for idx in range(self.applicationMainTabWidget.count())]

        #get list of true/false of matching titles to _tab_widget_name
        #with an optional number
        pattern = _tab_widget_name + ' \[[0-9]*\]'
        matches = [re.match(pattern, title) or title == _tab_widget_name
                   for title in titles]

        #reuse means we have to delete all matching tab widgets
        if _reuse == True:
            map(self.applicationMainTabWidget.removeTab, any_indexes(matches))

        #if have to be created a tab widget and there is
        #at least one, with the same title, already
        elif _reuse == False and any(matches) == True:
            #get a maximum number of existing tabs, if there is no number
            #attached to any tabs then the default is 1
            max_num = get_max_number_between_signs(titles, from_end=True,
                                                   default=1)
            #add next number to the tab title
            _tab_widget_name = '%s [%d]' % (_tab_widget_name, max_num + 1)

        self.applicationMainTabWidget.addTab(tabWidget, _tab_widget_name)
        self.applicationMainTabWidget.setCurrentWidget(tabWidget)

    def closeEvent(self, event):
        for idx in range(self.applicationMainTabWidget.count()):
            tabWidget = self.applicationMainTabWidget.widget(idx)
            if hasattr(tabWidget, 'beforeCloseTab'):
                tabWidget.beforeCloseTab()


def InformationWindow(parent=None, **params):
    (title, information) = __message__(parent=None, **params)
    QMessageBox.information(parent, title, information)


def ErrorWindow(parent=None, **params):
    (title, error) = __message__(parent=None, title_default='Error', **params)
    QMessageBox.information(parent, title, error, QMessageBox.Critical)


def QuestionWindow(buttons_list, parent=None, default_button=None, **params):
    (title, message) = __message__(parent=None, **params)
    box = QMessageBox(parent)
    if title:
        box.setWindowTitle(title)
    if message:
        box.setText(message)
    if default_button:
        box.setDefaultButton(default_button)
    box.setStandardButtons(or_values(buttons_list))
    return box.exec_()


def AreYouSureWindow(parent=None, default_button=QMessageBox.Yes, **params):
    ret = QuestionWindow([QMessageBox.Yes, QMessageBox.No],
                         parent,
                         default_button=default_button,
                         message='Are you sure ?', **params)
    return ret == QMessageBox.Yes


def __message__(parent=None, **params):
    local_params = Params(**params)
    if local_params.title_id == None and local_params.title_default == None \
        and local_params.title == None:
        title = "Information"
    else:
        title = QT_I18N(local_params.title_id,
                        _default=local_params.title if local_params.title \
                                        else local_params.title_default,
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
        self.lineNumberLabel = LabelCommon(self)
        self.preview = PlainTextEditCommon(self, readonly=True)

        closeButton = PushButtonCommon(self,
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


class MainTabItemWindow(MainWindowCommon):
    def __init__(self, parent, **params):
        super(MainTabItemWindow, self).__init__(parent, **params)
        self.__centralWidget__ = WidgetCommon(self,
                                    not_add_widget_to_parent_layout=True)
        self.setCentralWidget(self.__centralWidget__)
        self.__activity__ = ActivityDockWidget(self, not_closable=True,
                                               **params)
