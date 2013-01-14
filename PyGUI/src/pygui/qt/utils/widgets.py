'''
Created on 26-11-2012

@author: jurek
'''
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pygui.qt.utils.settings import Setter
from pygui.qt.utils.settings import SettingsFactory
from pygui.qt.utils.qt_i18n import text_I18N
from pygui.qt.utils.qt_i18n import title_I18N
from pycore.misc import Params
from pygui.qt.utils.logging import LoggingEventFilter
from pycore.globals import Globals
import inspect


def createComposite(parent=None, **params):
    return __item(parent, widget=QWidget(parent), **params)


def createLabel(parent=None, **params):
    if params.get('sizePolicy', None) == None:
        params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Preferred)
    return __item(parent, widget=QLabel(parent), textable=True, **params)


def createPushButton(parent=None, **params):
    if params.get('sizePolicy', None) == None:
        params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Fixed)
    return __item(parent, widget=__PushButton(parent), textable=True, **params)


def createGroupBox(parent=None, **params):
    return __item(parent, widget=QGroupBox(parent), titleable=True, **params)


def createLineEdit(parent=None, **params):
    return __item(parent, widget=__LineEditWidget(parent, **params), **params)


class LineEditWidget(QLineEdit):
    def __init__(self, parent, **params):
        QLineEdit.__init__(self, parent)
        params = Params(**params)
        self.focusEventHandler = params.focusEventHandler

    def focusInEvent(self, qfocusevent):
        if not self.focusEventHandler == None:
            self.focusEventHandler()
        super(LineEditWidget, self).focusInEvent(qfocusevent)


def createCheckBox(parent=None, **params):
    return __item(parent, widget=__CheckBox(parent), textable=True, **params)


def createTableView(parent=None, **params):
    return __item(parent, widget=__TableView(parent), **params)


def createSlider(parent=None, **params):
    return __item(parent, widget=QSlider(parent), **params)


def createTextEdit(parent=None, **params):
    return __item(parent, widget=QTextEdit(parent), **params)


def createPlainTextEdit(parent=None, **params):
    return __item(parent, widget=QPlainTextEdit(parent), **params)


def createProgressBar(parent=None, **params):
    return __item(parent, widget=QProgressBar(parent), **params)


def createButtonGroup(parent=None, **params):
    return __item(parent, widget=QButtonGroup(parent), **params)


def createTabWidget(parent=None, **params):
    return __item(parent, widget=QTabWidget(parent), **params)


def createWidget(parent=None, **params):
    return __item(parent, widget=QWidget(parent), **params)


def createSplitter(parent=None, **params):
    return __item(parent, widget=__Splitter(parent, **params), **params)


def createListWidget(parent=None, **params):
    return __item(parent, widget=__ListWidget(parent), **params)


def __item(parent=None, **params):
    """
    method to create a widget based o information contained in params
    dictionary, it is a factory method
    """
    parent_layout = parent.layout() \
                if not parent == None and not parent.layout() == 0 else None
    params = Params(**params)
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
    if parent and params.add_widget_to_parent == True:
        parent.addWidget(widget)
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


class __CheckBox(QCheckBox, Common):
    pass


class __PushButton(QPushButton, Common):
    pass


class __LineEditWidget(LineEditWidget, Common):
    pass


class __TableView(QTableView, Common):
    pass


class SplitterWidget(QSplitter):
    def __init__(self, parent, **params):
        QSplitter.__init__(self, parent)
        self.setHandleWidth(self.handleWidth() * 2)
        self.params = Params(**params)
        if self.params.save_state:
            SettingsFactory.loadSettings(self,
                    Setter(sizes_list=None,
                           _conv=QVariant.toPyObject,
                           _conv_2level=self.conv2level,
                           objectName=self.params.objectName
                           ))

    def destroySplitter(self):
        if self.params.save_state:
            SettingsFactory.saveSettings(self,
                                         Setter(sizes_list=self.sizes(),
                                            _no_conv=True,
                                            objectName=self.params.objectName))

    def conv2level(self, value):
        return None if value == None else [variant.toInt()[0]
                                           for variant in value]

    def sizesLoaded(self):
        return not self.sizes_list == None and len(self.sizes_list) > 0

    def updateSizes(self):
        if self.sizesLoaded():
            self.setSizes(self.sizes_list)


class __Splitter(SplitterWidget, Common):
    pass


class __ListWidget(QListWidget, Common):
    pass
