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
except ImportError as error:
    ImportErrorMessage(error)


class LoggingWindow(QDialog):
    def __init__(self, parent=None):
        super(LoggingWindow, self).__init__(parent)
        self.isClosed = False
        self.setModal(False)
        self.setWindowTitle('Logging')
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setLayout(QVBoxLayout())

        self.loggingWidget = QPlainTextEdit(self)
        self.textCursor = QTextCursor(self.loggingWidget.textCursor())
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.loggingWidget.setReadOnly(True)
        self.layout().addWidget(self.loggingWidget)

        operationalButtons = QWidget(self)
        operationalButtons.setLayout(QHBoxLayout())
        self.layout().addWidget(operationalButtons)

        clearButton = QPushButton("Clear", operationalButtons)
        self.connect(clearButton, SIGNAL("clicked()"), self.clearClicked)
        operationalButtons.layout().addWidget(clearButton)

        self.detailsButton = QCheckBox("Details",
                                          operationalButtons)
        operationalButtons.layout().addWidget(self.detailsButton)

        self.includeMethodsButton = QCheckBox("Includes __<name>__ methods",
                                          operationalButtons)
        operationalButtons.layout().addWidget(self.includeMethodsButton)

        self.closeHandler = None

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

    def normalOutputWritten(self, text):
        self.textCursor.movePosition(QTextCursor.End)
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


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        #self.textWritten.emit(str(text))
        self.textWritten.emit(QString(text))


class LoggingEventEater(QObject):

    LOGGING_WINDOW = None
    LOGGING_STARTED = False

    def __init__(self, _parent, _stack=inspect.stack()):
        super(LoggingEventEater, self).__init__(_parent)
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
                if LoggingEventEater.LOGGING_STARTED == True:
                    #print('Type: ' + str(type(event)))
                    #print('Dict: ' + str(dir(event)))
                    self.__formatOutput__(obj, event)
                    return True

        return super(LoggingEventEater, self).eventFilter(obj, event)

    def closeLoggingHandler(self):
        LoggingEventEater.LOGGING_STARTED = False

    def __formatOutput__(self, obj, event):
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

        if LoggingEventEater.LOGGING_WINDOW.details():
            print('')
            print('Object details start:')
            keys = dir(obj) \
                    if \
                        LoggingEventEater.LOGGING_WINDOW.includeMethods()\
                    else [key for key in dir(obj)
                          if not (key.startswith('__') and key.endswith('__'))]
            for key in keys:
                print('key: ' + key + ' value: ' + str(getattr(obj, key)))
            print('Object details stop')
            print('')

        print('%s' % '*' * 160)

    def createLoggingWindow(self):
        if LoggingEventEater.LOGGING_WINDOW == None or \
            LoggingEventEater.LOGGING_WINDOW.isClosed == True:
            LoggingEventEater.LOGGING_STARTED = True
            LoggingEventEater.LOGGING_WINDOW = LoggingWindow(
                                QApplication.instance().activeWindow())
            LoggingEventEater.LOGGING_WINDOW.setCloseHandler(
                                            self.closeLoggingHandler)
            LoggingEventEater.LOGGING_WINDOW.show()

            return True
        return False


LOGGING_EVENT_EATER = None


def log(parent, text):
    if Globals.DEBUG == True:
        if not LoggingEventEater.LOGGING_WINDOW:
            LoggingEventEater(parent).createLoggingWindow()
        LoggingEventEater.LOGGING_WINDOW.normalOutputWritten(text)
    else:
        print(text)
