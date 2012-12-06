'''
Created on 26-11-2012

@author: jurek
'''
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pygui.qt.utils.qt_i18n import text_I18N
from pygui.qt.utils.qt_i18n import title_I18N
from pycore.misc import Params
from pygui.qt.utils.threads import ThreadTask


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


def createPlainTextEdit(parent=None, **params):
    return __item(parent, widget=QPlainTextEdit(parent), **params)


def createProgressBar(parent=None, **params):
    return __item(parent, widget=QProgressBar(parent), **params)


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


class ProgressBarManager(object):

    def __init__(self, parent, **params):
        self.parent = parent
        self.params = Params(**params)
        self.progressBarComposite = createComposite(parent,
                                            layout=QHBoxLayout())
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.progressBar = createProgressBar(self.progressBarComposite,
                                             sizePolicy=sizePolicy)
        self.progressBar.setRange(0, 0)
        self.progressBar.setValue(0)
        if self.params.hidden == True:
            self.progressBarComposite.hide()

        self.stopButton = createPushButton(
                                self.progressBarComposite,
                                i18n="datasource.stop.progress.bar.button",
                                i18n_def="Stop")
        self.progressBarComposite.connect(self.stopButton,
                                          SIGNAL("clicked()"),
                                          self.stop)
        self.threadTask = None
        self.local_params = None

    def show(self):
        self.progressBarComposite.show()

    def hide(self, reset=True):
        self.progressBarComposite.hide()

    def reset(self):
        self.progressBar.reset()

    def setValue(self, value):
        self.progressBar.setValue(0)

    def tick(self):
        self.setValue(0)

    def start(self, **params):
        self.local_params = Params(**params)
        if self.local_params.before:
            self.local_params.before()

        if self.threadTask:
            self.threadTask.stop()
            self.threadTask.setTask(self.local_params.progressJob)
            self.threadTask.setUpdateTask(updateTaskName='taskUpdated',
                                          updateAction=self.tick)
            self.threadTask.setFinishTask(finishTaskName='taskFinished',
                                          finishAction=self.stop)
        else:

            self.threadTask = ThreadTask(self.parent,
                                        updateTaskName='taskUpdated',
                                        updateAction=self.tick,
                                        task=self.local_params.progressJob,
                                        finishTaskName='taskFinished',
                                        finishAction=self.stop)
        if self.threadTask:
            if self.params.hidden == True:
                self.show()
            self.reset()
            if not self.params.progressJob == None:
                self.threadTask.setTask(self.params.progressJob)
            if not self.local_params.progressJob == None:
                self.threadTask.setTask(self.local_params.progressJob)
            self.threadTask.start()

    def stop(self):
        if self.threadTask and self.threadTask.isStopped() == False:
            self.threadTask.stop()
        if not self.local_params == None:
            if not self.local_params.after == None:
                self.local_params.after()
        if self.params.hidden == True:
            self.hide()
        self.reset()

    def close(self):
        self.stop()
        if self.threadTask:
            self.threadTask.close()

    def isStopped(self):
        if not self.threadTask == None:
            return self.threadTask.isStopped()
        return True

    def update(self):
        if not self.threadTask == None:
            self.threadTask.emitUpdateTask()
