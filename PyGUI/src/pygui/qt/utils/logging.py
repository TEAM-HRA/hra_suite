'''
Created on 22-12-2012

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import sys
    import inspect
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.globals import Globals
    from pygui.qt.utils.specials import getWidgetFromStack
    from pygui.qt.utils.specials import getOrCreateTabFromMainTabWidgetStack
    from pygui.qt.utils.specials import StackObject
except ImportError as error:
    ImportErrorMessage(error, __name__)


__LOGGING_TAB_LABEL__ = "Logging"


class LoggingCommonWidget():
    """
    common functionality
    """
    def Init(self, parent):

        self.isClosed = False
        self.loggingWidget = QPlainTextEdit(parent)
        self.loggingWidget.installEventFilter(
                                        LoggingEventFilter(inspect.stack()))
        self.textCursor = QTextCursor(self.loggingWidget.textCursor())
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.loggingWidget.setReadOnly(True)
        parent.layout().addWidget(self.loggingWidget)

        operationalButtons = QWidget(parent)
        operationalButtons.setLayout(QHBoxLayout())
        operationalButtons.installEventFilter(
                                        LoggingEventFilter(inspect.stack()))
        parent.layout().addWidget(operationalButtons)

        clearButton = QPushButton("Clear", operationalButtons)
        clearButton.installEventFilter(
                                        LoggingEventFilter(inspect.stack()))
        self.connect(clearButton, SIGNAL("clicked()"), self.clearClicked)
        operationalButtons.layout().addWidget(clearButton)

        self.detailsButton = QCheckBox("Details",
                                          operationalButtons)
        self.detailsButton.installEventFilter(
                                        LoggingEventFilter(inspect.stack()))
        operationalButtons.layout().addWidget(self.detailsButton)

        self.includeMethodsButton = QCheckBox("Includes __<name>__ methods",
                                          operationalButtons)
        self.includeMethodsButton.installEventFilter(
                                        LoggingEventFilter(inspect.stack()))
        operationalButtons.layout().addWidget(self.includeMethodsButton)

        self.stopLoggingButton = QCheckBox("Stop logging",
                                          operationalButtons)
        self.stopLoggingButton.installEventFilter(
                                        LoggingEventFilter(inspect.stack()))
        operationalButtons.layout().addWidget(self.stopLoggingButton)

        self.closeHandler = None

        sys.stdout = __EmittingStream__(textWritten=self.normalOutputWritten)

    def normalOutputWritten(self, text):
        self.textCursor.movePosition(QTextCursor.End)
        if not hasattr(text, '__len__'):
            text = str(text)
        if hasattr(text, 'endswith') and not text.endswith('\n'):
            text = text + '\n'
        self.textCursor.insertText(text)
        self.loggingWidget.moveCursor(QTextCursor.End)

    def closeEvent(self, event):
        self.isClosed = True
        sys.stdout = sys.__stdout__
        if self.closeHandler:
            self.closeHandler()

    def clearClicked(self):
        self.loggingWidget.clear()

    def setCloseHandler(self, handler):
        self.closeHandler = handler

    def includeMethods(self):
        return (self.includeMethodsButton.checkState() == Qt.Checked)

    def details(self):
        return (self.detailsButton.checkState() == Qt.Checked)

    def stopLogging(self):
        return (self.stopLoggingButton.checkState() == Qt.Checked)


class LoggingWindowWidget(LoggingCommonWidget, QWidget):
    """
    logging window as a part of another parent widget
    """
    def __init__(self, parent=None):
        super(LoggingWindowWidget, self).__init__(parent)
        self.Init(parent)


class LoggingWindowDialog(LoggingCommonWidget, QDialog):
    """
    logging window as a separate dialog window
    """
    def __init__(self, parent=None):
        super(LoggingWindowDialog, self).__init__(parent)
        self.setModal(False)
        self.setWindowTitle('Logging')
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setLayout(QVBoxLayout())
        self.Init(self)


class __EmittingStream__(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        #self.textWritten.emit(str(text))
        self.textWritten.emit(QString(text))


class LoggingEventFilter(QObject):

    LOGGING_WINDOW = None
    LOGGING_STARTED = False

    def __init__(self, _stack=inspect.stack()):
        super(LoggingEventFilter, self).__init__(getWidgetFromStack(_stack))
        self.loggingWindowOpened = False
        self.loggingWindow = None
        self.logger = None
        self.stack = _stack

    def eventFilter(self, obj, event):
        #it seems to be strange but Qt.Key_Shift key code means right CTRL key
        if event.type() == QEvent.KeyPress \
            and event.nativeModifiers() == Qt.Key_Shift:

            return self.createLoggingWindow()

        elif event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                if LoggingEventFilter.LOGGING_STARTED == True:
                    #print('Type: ' + str(type(event)))
                    #print('Dict: ' + str(dir(event)))
                    self.__formatOutput__(obj, event)
                    return True

        return super(LoggingEventFilter, self).eventFilter(obj, event)

    def closeLoggingHandler(self):
        LoggingEventFilter.LOGGING_STARTED = False

    def __formatOutput__(self, obj, event):
        if LoggingEventFilter.LOGGING_WINDOW.stopLogging():
            return

        print('%s' % '*' * 160)
        print('Object id: %s class: %s' % (id(obj), obj.__class__))

        indent_num = 0
        for _stack in self.stack:
            frame = _stack[0]
            module_ = inspect.getmodule(frame)
            locals_ = frame.f_locals
            lineno_ = frame.f_lineno
            class_ = locals_.get('self')
            if class_:
                class_name = class_.__class__.__name__
            else:
                class_name = "<module>"
            indent_num = indent_num + 1
            print('%smodule: %s class: %s lineno: %i'
                      % ("  " * indent_num, module_, class_name, lineno_))

        if LoggingEventFilter.LOGGING_WINDOW.details():
            print('')
            print('Object details start:')
            keys = dir(obj) \
                    if \
                        LoggingEventFilter.LOGGING_WINDOW.includeMethods()\
                    else [key for key in dir(obj)
                          if not (key.startswith('__') and key.endswith('__'))]
            for key in keys:
                print('key: ' + key + ' value: ' + str(getattr(obj, key)))
            print('Object details stop')
            print('')

        print('%s' % '*' * 160)

    def createLoggingWindow(self):
        if LoggingEventFilter.LOGGING_WINDOW == None or \
            LoggingEventFilter.LOGGING_WINDOW.isClosed == True:
            LoggingEventFilter.LOGGING_STARTED = True

            stackObject = getOrCreateTabFromMainTabWidgetStack(
                                                    __LOGGING_TAB_LABEL__,
                                                    self.stack,
                                                    layout=QVBoxLayout())
            if stackObject.status == StackObject.ANY:
                LoggingEventFilter.LOGGING_WINDOW = LoggingWindowDialog(
                                                    stackObject._object)
            else:
                LoggingEventFilter.LOGGING_WINDOW = LoggingWindowWidget(
                                                    stackObject._object)
            LoggingEventFilter.LOGGING_WINDOW.setCloseHandler(
                                            self.closeLoggingHandler)
            LoggingEventFilter.LOGGING_WINDOW.show()

            return True
        return False


def log(text):
    if Globals.DEBUG == True:
        if not LoggingEventFilter.LOGGING_WINDOW:
            LoggingEventFilter().createLoggingWindow()
        LoggingEventFilter.LOGGING_WINDOW.normalOutputWritten(text)
    else:
        print(text)
