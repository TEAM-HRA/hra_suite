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

    def __init__(self, parent=None, **params):
        self.progressBarComposite = None
        self.threadTask = None
        if parent:
            self.setParams(parent, **params)

    def setParams(self, parent, **params):
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
        if self.progressBarComposite:
            self.progressBarComposite.show()

    def hide(self, reset=True):
        if self.progressBarComposite:
            self.progressBarComposite.hide()

    def reset(self):
        if self.progressBarComposite:
            self.progressBar.reset()

    def setValue(self, value):
        if self.progressBarComposite:
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
        if self.progressBarComposite == None:
            return
        if self.threadTask == None:
            return
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
        if self.progressBarComposite == None:
            return False
        if not self.threadTask == None:
            return self.threadTask.isStopped()
        return True

    def update(self):
        if self.threadTask:
            if self.isStopped() == False:
                self.threadTask.emitUpdateTask()
        return not self.isStopped()


class WidgetsHorizontalHeader(QHeaderView):
    """
    class for table header line used to create a header
    filled with widgets instead of simple texts
    widgets have to possess a layout
    """
    def __init__(self, parent, widgets):
        super(WidgetsHorizontalHeader, self).__init__(Qt.Horizontal, parent)

        #get optimal size for header line based on sizes of header widgets
        height = 0
        width = 0
        margin = 0
        for idx in range(len(widgets)):
            sizeHint = widgets[idx].sizeHint()
            if height < sizeHint.height():
                height = sizeHint.height()
            if width < sizeHint.width():
                width = sizeHint.width()
            if margin < widgets[idx].layout().margin():
                margin = widgets[idx].layout().margin()

        #very import property used in sizeHint method
        self.sizeHint = QSize(width + margin, height + margin)

        self.setResizeMode(QHeaderView.Interactive)
        parent.setHorizontalHeader(self)
        self.widgets = widgets
        for idx in range(len(self.widgets)):
            widgets[idx].setParent(self)
            x = self.sectionPosition(idx)
            y = 0
            w = widgets[idx].sizeHint().width()  # self.sectionSize(idx)
            h = height
            widgets[idx].setGeometry(QRect(x, y, w, h))

        #if a header (or section) changes then widgets have to be moved
        self.connect(self,
                     SIGNAL("sectionResized(int,int,int)"),
                     self.sectionResized)

    def sizeHint(self):
        """
        very important method without it no widgets are displayed
        """
        return self.sizeHint

    def sectionResized(self, logicalIndex, oldSize, newSize):
        """
        a section means one header
        """
        old = self.widgets[logicalIndex].geometry()
        self.widgets[logicalIndex].setGeometry(old.x(), old.y(),
                                               newSize, old.height())
        #have to move the following headers about difference
        #between old and new size
        for idx in range(logicalIndex + 1, len(self.widgets)):
            self.changeXForHeader(idx, newSize - oldSize)

    def changeXForHeader(self, logicalIndex, x):
        """
        parameter x could be positive move to right
        or negative move to left
        """
        old = self.widgets[logicalIndex].geometry()
        self.widgets[logicalIndex].setGeometry(old.x() + x, old.y(),
                                            old.width(), old.height())
