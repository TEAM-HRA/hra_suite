'''
Created on 26-11-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import inspect
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pygui.qt.utils.qt_i18n import text_I18N
    from pygui.qt.utils.qt_i18n import title_I18N
    from pycore.misc import Params
    from pygui.qt.utils.logging import LoggingEventFilter
    from pycore.globals import Globals
    from pygui.qt.utils.signals import LIST_ITEM_CLICKED_SIGNAL
except ImportError as error:
    ImportErrorMessage(error, __name__)


def createComposite(parent=None, **params):
    return item(parent=parent, widget=QWidget(parent), **params)


def createGroupBox(parent=None, **params):
    return item(parent=parent, widget=QGroupBox(parent), titleable=True, **params) # @IgnorePep8


def createLineEdit(parent=None, **params):
    return item(parent=parent, widget=__LineEditWidget(parent, **params), **params) # @IgnorePep8


class LineEditWidget(QLineEdit):
    def __init__(self, parent, **params):
        QLineEdit.__init__(self, parent)
        params = Params(**params)
        self.focusEventHandler = params.focusEventHandler

    def focusInEvent(self, qfocusevent):
        if not self.focusEventHandler == None:
            self.focusEventHandler()
        super(LineEditWidget, self).focusInEvent(qfocusevent)


def createTableView(parent=None, **params):
    return item(parent=parent, widget=__TableView(parent), **params)


def createSlider(parent=None, **params):
    return item(parent=parent, widget=QSlider(parent), **params)


def createTextEdit(parent=None, **params):
    return item(parent=parent, widget=QTextEdit(parent), **params)


def createPlainTextEdit(parent=None, **params):
    return item(parent=parent, widget=QPlainTextEdit(parent), **params)


def createProgressBar(parent=None, **params):
    return item(parent=parent, widget=QProgressBar(parent), **params)


def createButtonGroup(parent=None, **params):
    return item(parent=parent, widget=QButtonGroup(parent), **params)


def item(**params):
    """
    method to create a widget based o information contained in
    a parameter params dictionary, it is a factory method
    """
    params = Params(**params)
    parent_layout = params.parent.layout() \
                if not params.parent == None and \
                not params.parent.layout() == 0 else None

    widget = params.widget
    __set_widget_size(widget, params.size, params.width, params.height)
    if not params.enabled == None:
        widget.setEnabled(params.enabled)
    if not params.selectionBehavior == None:
        widget.setSelectionBehavior(params.selectionBehavior)
    if not params.selectionMode == None:
        widget.setSelectionMode(params.selectionMode)
    if not params.sizePolicy == None:
        widget.setSizePolicy(params.sizePolicy)
    if not params.layout == None:
        widget.setLayout(params.layout)
    if not params.readonly == None:
        widget.setReadOnly(params.readonly)
    if not params.orientation == None:
        widget.setOrientation(params.orientation)
    if params.maxLength:
        widget.setMaxLength(params.maxLength)
    if not params.checked == None:
        widget.setChecked(params.checked)
    added = None
    if not params.alignment == None:
        added = __create_inner_alignment_layout(parent_layout, widget,
                                                params.alignment)
        if not added and not params.layout == None:
            params.layout.setAlignment(params.alignment)

    if not added and not parent_layout == None:
        if not params.not_add_widget_to_parent_layout == True and \
            isinstance(widget, QWidget):
            parent_layout.addWidget(widget)

    if not params.stretch_after_widget == None:
        if not parent_layout == None:
            parent_layout.addStretch(params.stretch_after_widget)
    if params.titleable and (params.i18n or params.i18n_def):
        title_I18N(widget, params.i18n, params.i18n_def)
    if params.textable and (params.i18n or params.i18n_def):
        text_I18N(widget, params.i18n, params.i18n_def)
    if not params.text == None:
        widget.setText(params.text)
    if not params.hidden == None:
        widget.setHidden(params.hidden)
    if Globals.DEBUG == True:
        #very important parameter inspect.stack()
        #which set up properly caller's stack of a created widget
        widget.installEventFilter(LoggingEventFilter(inspect.stack()))
    if not params.object_name == None:
        widget.setObjectName(params.object_name)
    if not params.clicked_handler == None:
        widget.connect(widget, SIGNAL("clicked()"), params.clicked_handler)
    if not params.enabled_precheck_handler == None:
        widget.setEnabledPrecheckHandler(params.enabled_precheck_handler)
    if not params.close_handler == None:
        widget.connect(widget, SIGNAL("closeEvent()"), params.close_handler)
    if not params.list_item_clicked_handler == None:
        widget.connect(widget, LIST_ITEM_CLICKED_SIGNAL,
                       params.list_item_clicked_handler)
    if params.parent and params.add_widget_to_parent == True:
        params.parent.addWidget(widget)
    return widget


def __create_inner_alignment_layout(parent_layout, widget, alignment):
    """
    method which creates, if necessary, inner layout suitable
    to employ effectively alignment parameter
    """
    inner_layout = None
    if alignment in (Qt.AlignLeft, Qt.AlignCenter, Qt.AlignRight) \
        and not isinstance(parent_layout, QHBoxLayout):
        inner_layout = QHBoxLayout()
    elif alignment in (Qt.AlignTop, Qt.AlignVCenter, Qt.AlignBottom) \
        and not isinstance(parent_layout, QVBoxLayout):
        inner_layout = QVBoxLayout()
    if not inner_layout == None:
        inner_layout.setAlignment(alignment)
        inner_layout.addWidget(widget)
        if not parent_layout == None:
            parent_layout.addLayout(inner_layout)
    return not inner_layout == None


def __set_widget_size(widget, size, width, height):
    if not size == None or not width == None or not height == None:
        if not width == None and height == None:
            widget.setFixedWidth(width)
        elif width == None and not height == None:
            widget.setFixedHeight(height)
        elif not width == None and not height == None:
            widget.setFixedHeight(width, height)
        else:
            widget.setFixedSize(size)

ENABLED_SIGNAL_NAME = 'enabled_signal(bool)'


class Common(QObject):
    """
    the class Common is the main functionality which set up
    a connection between the signal and created widget, and also invokes
    handler passed as enabled_precheck_handler parameter
    """
    def setEnabledPrecheckHandler(self, enabled_precheck_handler):
        self.enabled_precheck_handler = enabled_precheck_handler
        self.__connectHandler__(self.enabled_precheck_handler,
                                ENABLED_SIGNAL_NAME,
                                self.__enabled_handler__)

    def __connectHandler__(self, _widget_or_handler, signal_name, slot_handler): # @IgnorePep8
        obj_ = None
        if hasattr(_widget_or_handler, '__self__'):
            # this means that _widget_or_handler is a method we need a object
            # associated with this method
            obj_ = _widget_or_handler.__self__
        else:
            # this means that _widget_or_handler is an object not a method
            obj_ = _widget_or_handler
        self.connect(obj_, SIGNAL(signal_name), slot_handler)

    @pyqtSlot(bool)
    def __enabled_handler__(self, enabled):
        precheck_enabled = self.enabled_precheck_handler(self)
        self.setEnabled(enabled
                    if precheck_enabled == None else precheck_enabled)


class __LineEditWidget(LineEditWidget, Common):
    pass


class __TableView(QTableView, Common):
    pass


class WidgetCommon(QWidget, Common):
    def __init__(self, parent, **params):
        super(WidgetCommon, self).__init__(parent)
        item(parent=parent, widget=self, **params)


class __ListWidget(QListWidget, Common):
    pass


def close_tab_widget(tab_widget_parent, tab_widget):
    """
    method which closes specified tab
    """
    if hasattr(tab_widget, 'beforeCloseTab'):
        tab_widget.beforeCloseTab()
    idx = tab_widget_parent.indexOf(tab_widget)
    tab_widget_parent.removeTab(idx)


class TabWidgetCallableCloseHandler(object):
    """
    class used as a callable object to close tab widget item
    """
    def __init__(self, tab_widget_parent, tab_widget):
        self.tab_widget_parent = tab_widget_parent
        self.tab_widget = tab_widget

    def __call__(self):
        close_tab_widget(self.tab_widget_parent, self.tab_widget)


class TabWidgetCommon(QTabWidget, Common):
    def __init__(self, parent, **params):
        super(TabWidgetCommon, self).__init__(parent)
        item(parent=parent, widget=self, **params)

    def closeTab(self, widget):
        close_tab_widget(self, widget)

    def tabExists(self, objectName):
        for idx in range(self.count()):
            if objectName == self.widget(idx).objectName():
                return True
        return False


class TabWidgetItemCommon(QWidget, Common):
    def __init__(self, **params):
        self.params = Params(**params)
        super(TabWidgetItemCommon, self).__init__(self.params.parent)
        item(widget=self, **params)

    def closeTab(self):
        #self.params.parent has to be a QTabWidget object
        close_tab_widget(self.params.parent, self)


class LabelCommon(QLabel, Common):
    def __init__(self, parent, **params):
        super(LabelCommon, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Preferred)
        item(parent=parent, widget=self, textable=True, **params)


class MainWindowCommon(QMainWindow, Common):
    def __init__(self, parent, **params):
        super(MainWindowCommon, self).__init__(parent)
        item(parent=parent, widget=self, **params)


class StatusBarCommon(QStatusBar, Common):
    def __init__(self, parent, **params):
        super(StatusBarCommon, self).__init__(parent)
        item(parent=parent, widget=self, **params)


class ListWidgetCommon(QListWidget, Common):
    def __init__(self, parent, **params):
        super(ListWidgetCommon, self).__init__(parent)
        item(parent=parent, widget=self, **params)


class PushButtonCommon(QPushButton, Common):
    def __init__(self, parent, **params):
        super(PushButtonCommon, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                               QSizePolicy.Fixed)
        item(parent=parent, widget=self, textable=True, **params)


class CheckBoxCommon(QCheckBox, Common):
    def __init__(self, parent, **params):
        super(CheckBoxCommon, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                               QSizePolicy.Fixed)
        item(parent=parent, widget=self, textable=True, **params)

    def isChecked(self):
        return self.checkState() == Qt.Checked
