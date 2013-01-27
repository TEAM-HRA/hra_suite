'''
Created on 26-11-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import inspect
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.globals import Globals
    from pycore.misc import Params
    from pycore.introspection import get_object
    from pycore.collections import nvl
    from pygui.qt.utils.qt_i18n import text_I18N
    from pygui.qt.utils.qt_i18n import title_I18N
    from pygui.qt.utils.logging import LoggingEventFilter
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.utils.signals import LIST_ITEM_CLICKED_SIGNAL
    from pygui.qt.utils.signals import LIST_ITEM_DOUBLE_CLICKED_SIGNAL
except ImportError as error:
    ImportErrorMessage(error, __name__)


def prepareWidget(**params):
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


class WidgetCommon(QWidget, Common):
    def __init__(self, parent, **params):
        super(WidgetCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class LabelCommon(QLabel, Common):
    def __init__(self, parent, **params):
        super(LabelCommon, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                           QSizePolicy.Preferred)
        prepareWidget(parent=parent, widget=self, textable=True, **params)


class MainWindowCommon(QMainWindow, Common):
    def __init__(self, parent, **params):
        super(MainWindowCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class StatusBarCommon(QStatusBar, Common):
    def __init__(self, parent, **params):
        super(StatusBarCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class ListWidgetCommon(QListWidget, Common):
    def __init__(self, parent, **params):
        super(ListWidgetCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)
        double_click_handler = params.get('list_item_double_clicked_handler',
                                          None)
        if double_click_handler:
            self.connect(self, LIST_ITEM_DOUBLE_CLICKED_SIGNAL,
                         double_click_handler)


class PushButtonCommon(QPushButton, Common):
    def __init__(self, parent, **params):
        super(PushButtonCommon, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                               QSizePolicy.Fixed)
        prepareWidget(parent=parent, widget=self, textable=True, **params)


class CheckBoxCommon(QCheckBox, Common):
    def __init__(self, parent, **params):
        super(CheckBoxCommon, self).__init__(parent)
        if params.get('sizePolicy', None) == None:
            params['sizePolicy'] = QSizePolicy(QSizePolicy.Fixed,
                                               QSizePolicy.Fixed)
        prepareWidget(parent=parent, widget=self, textable=True, **params)


class LineEditCommon(QLineEdit, Common):
    def __init__(self, parent, **params):
        QLineEdit.__init__(self, parent)
        self.focusEventHandler = params.get('focusEventHandler', None)
        prepareWidget(parent=parent, widget=self, **params)

    def focusInEvent(self, qfocusevent):
        if not self.focusEventHandler == None:
            self.focusEventHandler()
        super(LineEditCommon, self).focusInEvent(qfocusevent)


class CompositeCommon(WidgetCommon):
    """
    this a placeholder used as a generic widget which could contains other
    widgets
    """
    pass


class GroupBoxCommon(QGroupBox, Common):
    def __init__(self, parent, **params):
        super(GroupBoxCommon, self).__init__(parent)
        prepareWidget(parent=parent, titleable=True, widget=self, **params)


class TableViewCommon(QTableView, Common):
    def __init__(self, parent, **params):
        super(TableViewCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class SliderCommon(QSlider, Common):
    def __init__(self, parent, **params):
        super(SliderCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class TextEditCommon(QTextEdit, Common):
    def __init__(self, parent, **params):
        super(TextEditCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class PlainTextEditCommon(QPlainTextEdit, Common):
    def __init__(self, parent, **params):
        super(PlainTextEditCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class ProgressBarCommon(QProgressBar, Common):
    def __init__(self, parent, **params):
        super(ProgressBarCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class ButtonGroupCommon(QButtonGroup, Common):
    def __init__(self, parent, **params):
        super(ButtonGroupCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)


class DockWidgetCommon(QDockWidget, Common):
    def __init__(self, parent, **params):
        super(DockWidgetCommon, self).__init__(
                            nvl(params.get('title', None), ''), parent)
        if params.get('not_add_widget_to_parent_layout', None) == None:
            params['not_add_widget_to_parent_layout'] = True
        prepareWidget(parent=parent, widget=self, **params)
        self.params = Params(**params)

    def closeEvent(self, event):
        if self.params.not_closable:
            event.ignore()


class ListWidgetItemCommon(QListWidgetItem):
    def __init__(self, parent, **params):
        params = Params(**params)
        super(ListWidgetItemCommon, self).__init__(
                                            nvl(params.text, ''), parent)
        #store in data buffer of list item for later use
        if params.data:
            self.setData(Qt.UserRole, QVariant(params.data))

    def getData(self):
        item = self.data(Qt.UserRole)
        if item:
            return item.toPyObject()


class ApplicationCommon(QApplication):
    def __init__(self, *params):
        super(ApplicationCommon, self).__init__(*params)
        #set up main dispatcher as a QApplication object
        SignalDispatcher.setMainDispatcher(self)

        #set up USE_NUMPY_EQUIVALENT property
        if Globals.USE_NUMPY_EQUIVALENT:
            NUMPY_UTILS = get_object("pymath.utils.utils")
            if NUMPY_UTILS:
                if hasattr(NUMPY_UTILS, 'USE_NUMPY_EQUIVALENT'):
                    setattr(NUMPY_UTILS, 'USE_NUMPY_EQUIVALENT',
                            Globals.USE_NUMPY_EQUIVALENT)
