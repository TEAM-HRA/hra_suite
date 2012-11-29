'''
Created on 26-11-2012

@author: jurek
'''
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pygui.qt.utils.qt_i18n import text_I18N
from pygui.qt.utils.qt_i18n import title_I18N


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
    return __item(parent, widget=QPushButton(parent), textable=True, **params)


def createGroupBox(parent=None, **params):
    return __item(parent, widget=QGroupBox(parent), titleable=True, **params)


def createLineEdit(parent=None, **params):
    return __item(parent, widget=QLineEdit(parent), **params)


def createCheckBox(parent=None, **params):
    return __item(parent, widget=QCheckBox(parent), textable=True, **params)


def createTableView(parent=None, **params):
    return __item(parent, widget=QTableView(parent), **params)


def createSlider(parent=None, **params):
    return __item(parent, widget=QSlider(parent), **params)


def createTextEdit(parent=None, **params):
    return __item(parent, widget=QTextEdit(parent), **params)


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
    if params.enabled == False:
        widget.setEnabled(params.enabled)
    if not params.selectionBehavior == None:
        widget.setSelectionBehavior(params.selectionBehavior)
    if not params.selectionMode == None:
        widget.setSelectionMode(params.selectionMode)
    if not params.sizePolicy == None:
        widget.setSizePolicy(params.sizePolicy)
    if not params.layout == None:
        widget.setLayout(params.layout)
    if not params.orientation == None:
        widget.setOrientation(params.orientation)
    if params.maxLength:
        widget.setMaxLength(params.maxLength)
    added = None
    if not params.alignment == None:
        added = __create_inner_alignment_layout(parent_layout, widget,
                                                params.alignment)
        if not added and not params.layout == None:
            params.layout.setAlignment(params.alignment)

    if not added and not parent_layout == None:
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


class Params(object):
    """
    class which represents dictionary parameters
    by object where elements are accessible with dot notation
    if client tries to access not existing element then None value is returned
    """
    def __init__(self, **params):
        for param in params:
            setattr(self, param, params[param])

    # if parameter is not set in the __init__() method then returns None
    def __getattr__(self, name):
        return None
