'''
Created on 22-12-2012

@author: jurek
'''
import sys
import inspect
from Queue import LifoQueue
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport


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

        self.includeMethodsButton = QCheckBox("Includes __<name>__ methods",
                                          operationalButtons)
        self.connect(clearButton, SIGNAL("clicked()"),
                     self.includeMethodsClicked)
        operationalButtons.layout().addWidget(self.includeMethodsButton)

        self.closeHandler = None
        self.includeMethods = False

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

    def includeMethodsClicked(self):
        self.includeMethods = (self.includeMethodsButton.checkState()
                               == Qt.Checked)


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        #self.textWritten.emit(str(text))
        self.textWritten.emit(QString(text))


class LoggingEventEater(QObject):

    LOGGING_WINDOW = None
    LOGGING_STARTED = False

    def __init__(self, _parent):
        super(LoggingEventEater, self).__init__(_parent)
        self.loggingWindowOpened = False
        self.loggingWindow = None
        self.logger = None

    def eventFilter(self, obj, event):
        #it seems to be strange but Qt.Key_Shift key code means right CTRL key
        if event.type() == QEvent.KeyPress \
            and event.nativeModifiers() == Qt.Key_Shift:

            if LoggingEventEater.LOGGING_WINDOW == None or \
                LoggingEventEater.LOGGING_WINDOW.isClosed == True:
                LoggingEventEater.LOGGING_STARTED = True
                LoggingEventEater.LOGGING_WINDOW = LoggingWindow(
                                    QApplication.instance().activeWindow())
                LoggingEventEater.LOGGING_WINDOW.setCloseHandler(
                                                self.closeLoggingHandler)
                LoggingEventEater.LOGGING_WINDOW.show()

                return True
        elif event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                if LoggingEventEater.LOGGING_STARTED == True:
                    #print('Type: ' + str(type(event)))
                    #print('Dict: ' + str(dir(event)))
                    self.__formatOutput__(obj)
                    return True

        return super(LoggingEventEater, self).eventFilter(obj, event)

    def closeLoggingHandler(self):
        LoggingEventEater.LOGGING_STARTED = False

    def __formatOutput__(self, obj):
        print('%s' % '*' * 40)
        print('Object id: %s class: %s' % (id(obj), obj.__class__))

        if hasattr(obj, 'parentWidget') or hasattr(obj, 'nativeParentWidget'):
            parents = LifoQueue()
            print('Parents tree:')
            parent = obj.parentWidget()
            while not (parent == 0 or parent == None):
                parents.put(parent)
                parent = parent.parentWidget()

            indent_num = 0
            while not parents.empty():
                parent = parents.get()
                print('%sparent id: %s class: %s module: %s'
                      % ("  " * indent_num, id(parent),
                         parent.__class__, inspect.getmodule(parent)))
                indent_num = indent_num + 1

        #(filename, lineno, function, code_context, index) = \
        #    inspect.getframeinfo(inspect.currentframe())
        #print('filename %s' % (filename))

        #inspect.stack(inspect.currentframe())
