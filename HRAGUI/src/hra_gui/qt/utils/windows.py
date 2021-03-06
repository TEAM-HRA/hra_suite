'''
Created on 13-12-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
try:
    import sys
    import re
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from hra_core.misc import Params
    from hra_core.misc import get_max_number_between_signs
    from hra_core.collections_utils import any_indexes
    from hra_core.collections_utils import or_values
    from hra_core.collections_utils import nvl
    from hra_core.globals import GLOBALS
    from hra_core.introspection import get_class_object
    from hra_core.io_utils import normalize_filenames
    from hra_gui.qt.utils.qt_i18n import QT_I18N
    from hra_gui.qt.utils.signals import ADD_TAB_ITEM_WIDGET_SIGNAL
    from hra_gui.qt.activities.activities import ActivityDockWidget
    from hra_gui.qt.menu.menus import QTMenuBuilder
    from hra_gui.qt.widgets.commons import CommonWidget
    from hra_gui.qt.widgets.label_widget import LabelWidget
    from hra_gui.qt.widgets.push_button_widget import PushButtonWidget
    from hra_gui.qt.widgets.composite_widget import CompositeWidget
    from hra_gui.qt.widgets.plain_text_edit_widget import PlainTextEditWidget
    from hra_gui.qt.widgets.main_window_widget import MainWindowWidget
    from hra_gui.qt.custom_widgets.tabwidget import TabWidgetCommon
    from hra_gui.qt.custom_widgets.progress_bar import ProgressDialogManager
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ApplicationMainWindow(MainWindowWidget):

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

        self.connect(self, ADD_TAB_ITEM_WIDGET_SIGNAL, self.addTabWidget)

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


def AreYouSureWindow(parent=None, **params):
    default_button = nvl(params.get('default_button', None), QMessageBox.Yes)
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


def showFilesPreviewDialog(filespaths, parent=None):
    if filespaths == None or len(filespaths) == 0:
        InformationWindow(message="No files selected !")
    else:
        dialog = FilesPreviewDialog(normalize_filenames(filespaths), parent)
        dialog.exec_()


class FilesPreviewDialog(QDialog):

    def __init__(self, filesnames, parent=None):
        super(FilesPreviewDialog, self).__init__(parent)
        self.setWindowTitle('File(s) preview')
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setLayout(QVBoxLayout())
        #a list object has attribute 'insert'
        filesnames = filesnames if hasattr(filesnames, 'insert') \
                        else [filesnames]

        filesPreviewTabWidget = TabWidgetCommon(self)
        progressManager = ProgressDialogManager(self,
                                        label_text="Opening files ...",
                                        max_value=len(filesnames))
        with progressManager as progress:
            for filename in filesnames:
                if (progress.wasCanceled()):
                    break
                progress.increaseCounter()
                tab = self.__createFilePreview__(filesPreviewTabWidget,
                                                 filename)
                filesPreviewTabWidget.addTab(tab, 'File: ' + filename)

        closeButton = PushButtonWidget(self, i18n="close", i18n_def="Close")
        self.connect(closeButton, SIGNAL("clicked()"), self, SLOT("reject()"))

    def __createFilePreview__(self, parent, filename):
        composite = CompositeWidget(parent)
        layout = QVBoxLayout()
        composite.setLayout(layout)
        informationLabel = LabelWidget(composite)
        layout.addWidget(informationLabel)
        preview = PlainTextEditWidget(composite, readonly=True)
        layout.addWidget(preview)
        file_ = QFile(filename)
        if file_.open(QFile.ReadOnly):
            preview.insertPlainText(QString(file_.readAll()))
            preview.moveCursor(QTextCursor.Start)
            informationLabel.setText('Lines # '
                                     + str(preview.document().lineCount()))
            file_.close()
        return composite


class MainTabItemWindow(MainWindowWidget):
    def __init__(self, parent, **params):
        super(MainTabItemWindow, self).__init__(parent, **params)
        self.__centralWidget__ = CommonWidget(self,
                                    not_add_widget_to_parent_layout=True)
        self.setCentralWidget(self.__centralWidget__)
        self.__activity__ = ActivityDockWidget(self, not_closable=True,
                                               **params)
