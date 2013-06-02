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
    from pygui.qt.utils.qt_i18n import text_I18N
    from pygui.qt.utils.qt_i18n import title_I18N
    from pygui.qt.utils.logging import LoggingEventFilter
    from pygui.qt.utils.signals import LIST_ITEM_CLICKED_SIGNAL
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


class CommonWidget(QWidget, Common):
    def __init__(self, parent, **params):
        super(CommonWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)
        self.params = Params(**params)

    def hideEvent(self, event):
        if self.params.hide_event_handler:
            self.params.hide_event_handler(event)
        super(CommonWidget, self).hideEvent(event)


def maximize_widget(widget):
    """
    function to maximize a widget
    """
    if hasattr(widget, 'parent'):
        parent = widget.parent()
        if hasattr(parent, 'children'):
            for childWidget in parent.children():
                if widget == childWidget:
                    continue
                if hasattr(childWidget, 'hide'):
                    childWidget.hide()


def restore_widget(widget):
    """
    function to restore a widget
    """
    if hasattr(widget, 'parent'):
        parent = widget.parent()
        if hasattr(parent, 'children'):
            for childWidget in parent.children():
                if not widget == childWidget:
                    if hasattr(childWidget, 'show'):
                        childWidget.show()


def get_all_children(qwidget, all_children=None):
    """
    function to get all children for a qwidget
    """
    if all_children == None:
        all_children = []
    if qwidget.isWidgetType():
        children = qwidget.children()
        if len(children) == 0:
            return all_children
        all_children[len(all_children):] = children
        for child in qwidget.children():
            get_all_children(child, all_children)
    return all_children
