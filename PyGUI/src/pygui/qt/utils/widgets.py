'''
Created on 26-11-2012

@author: jurek
'''
import inspect
import collections
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pygui.qt.utils.qt_i18n import text_I18N
from pygui.qt.utils.qt_i18n import title_I18N
from pycore.misc import Params
from pygui.qt.utils.logging import LoggingEventFilter
from pycore.globals import Globals
from pygui.qt.utils.signals import LIST_ITEM_CLICKED_SIGNAL
from pycore.collections import all_true_values
from pycore.collections import nvl
from pycommon.actions import ActionSpec
from pygui.qt.actions.actions_utils import create_action


def createComposite(parent=None, **params):
    return item(parent, widget=QWidget(parent), **params)


def createPushButton(parent=None, **params):
    if params.get('sizePolicy', None) == None:
        params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Fixed)
    return item(parent, widget=__PushButton(parent), textable=True, **params)


def createGroupBox(parent=None, **params):
    return item(parent, widget=QGroupBox(parent), titleable=True, **params)


def createLineEdit(parent=None, **params):
    return item(parent, widget=__LineEditWidget(parent, **params), **params)


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
    return item(parent, widget=__CheckBox(parent), textable=True, **params)


def createTableView(parent=None, **params):
    return item(parent, widget=__TableView(parent), **params)


def createSlider(parent=None, **params):
    return item(parent, widget=QSlider(parent), **params)


def createTextEdit(parent=None, **params):
    return item(parent, widget=QTextEdit(parent), **params)


def createPlainTextEdit(parent=None, **params):
    return item(parent, widget=QPlainTextEdit(parent), **params)


def createProgressBar(parent=None, **params):
    return item(parent, widget=QProgressBar(parent), **params)


def createButtonGroup(parent=None, **params):
    return item(parent, widget=QButtonGroup(parent), **params)


def createListWidget(parent=None, **params):
    return item(parent, widget=__ListWidget(parent), **params)


def item(parent=None, **params):
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
    if not params.list_item_clicked_handler == None:
        widget.connect(widget, LIST_ITEM_CLICKED_SIGNAL,
                       params.list_item_clicked_handler)
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


class WidgetCommon(QWidget, Common):
    def __init__(self, parent, **params):
        super(WidgetCommon, self).__init__(parent)
        item(parent, widget=self, **params)


class ToolBarCommon(QToolBar, Common):
    def __init__(self, parent, _button_types=[], _check_fields=[], **params):
        super(ToolBarCommon, self).__init__(parent)
        item(parent, widget=self, **params)

        #to avoid some weird behaviour which manifests in including
        #in this toolbar buttons from the previous one
        button_types = _button_types[:]

        button_type_classes = [_button.__class__ for _button in button_types]
        for _class in ToolButtonType.__subclasses__():  # @UndefinedVariable
            button_type = _class()
            if _class not in button_type_classes and \
                (all_true_values(button_type, _check_fields) or
                 len(_check_fields) == 0):
                button_types.append(button_type)

        for _button_type in button_types:
            create_toolbar_button(parent, self, _button_type, **params)


class __ListWidget(QListWidget, Common):
    pass


class TabWidgetCommon(QTabWidget, Common):
    def __init__(self, parent, **params):
        super(TabWidgetCommon, self).__init__(parent)
        item(parent, widget=self, **params)


class LabelCommon(QLabel, Common):
    def __init__(self, parent, **params):
        super(LabelCommon, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Preferred)
        item(parent, widget=self, textable=True, **params)


class MainWindowCommon(QMainWindow, Common):
    def __init__(self, parent, **params):
        super(MainWindowCommon, self).__init__(parent)
        item(parent, widget=self, **params)


class StatusBarCommon(QStatusBar, Common):
    def __init__(self, parent, **params):
        super(StatusBarCommon, self).__init__(parent)
        item(parent, widget=self, **params)

DefaultToolButtonType = collections.namedtuple('ToolButtonType',
                    'active operational checkable handler_name icon_id title')


def create_toolbar_button(parent, toolbar, button_type, **params):
    params = Params(**params)
    if params.handler == None and button_type.handler_name:
        if hasattr(parent, button_type.handler_name):
            params.handler = getattr(parent, button_type.handler_name)
        elif hasattr(parent.parentWidget(), button_type.handler_name):
            params.handler = getattr(parent.parentWidget(),
                                     button_type.handler_name)
        elif hasattr(params, button_type.handler_name):
            params.handler = getattr(params, button_type.handler_name)
    title = nvl(params.button_title, button_type.title)
    actionSpec = ActionSpec(iconId=button_type.icon_id,
                                 handler=params.handler,
                                 title=title)
    toolbar.addWidget(ToolButtonCommon(toolbar,
                        action=create_action(toolbar, actionSpec)))


class ToolButtonType(object):
    def __init__(self, default, **params):
        params = Params(**params)
        self.active = nvl(params.active, default.active)
        self.operational = nvl(params.operational, default.operational)
        self.checkable = nvl(params.checkable, default.checkable)
        self.handler_name = nvl(params.handler_name, default.handler_name)
        self.icon_id = nvl(params.icon_id, default.icon_id)
        self.title = nvl(params.title, default.title)


class MaximumToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, True, False,
            'toolbar_maximum_handler', 'toolbar_maximum_button', 'Maximize')
        super(MaximumToolButton, self).__init__(default, **params)


class MinimumToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, True, False,
            'toolbar_minimum_handler', 'toolbar_minimum_button', 'Minimize')
        super(MinimumToolButton, self).__init__(default, **params)


class CloseToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, True, False,
            'toolbar_close_handler', 'toolbar_close_button', 'Close')
        super(CloseToolButton, self).__init__(default, **params)


class HideToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, True, False,
            'toolbar_hide_handler', 'toolbar_hide_button', 'Hide')
        super(HideToolButton, self).__init__(default, **params)


class CheckToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, False, True,
            'toolbar_check_handler', 'toolbar_check_button', 'Check')
        super(CheckToolButton, self).__init__(default, **params)


class UncheckToolButton(ToolButtonType):
    def __init__(self, **params):
        default = DefaultToolButtonType(True, False, True,
            'toolbar_uncheck_handler', 'toolbar_uncheck_button', 'Uncheck')
        super(UncheckToolButton, self).__init__(default, **params)


class ToolButtonCommon(QToolButton, Common):

    def __init__(self, parent, **params):
        super(ToolButtonCommon, self).__init__(parent)
        if params.get('add_widget_to_parent', None) == None:
            params['add_widget_to_parent'] = False
        if params.get('not_add_widget_to_parent_layout', None) == None:
            params['not_add_widget_to_parent_layout'] = True
        item(parent, widget=self, **params)
        action = params.get('action', None)
        if action:
            self.setDefaultAction(action)
