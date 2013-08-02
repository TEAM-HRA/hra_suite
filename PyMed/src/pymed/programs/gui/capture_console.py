import sys
from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport


class Window(QWidget):

    def __init__(self):

        QWidget.__init__(self)

        self.textBrowser = QTextBrowser(self)
        self.lineEdit = QLineEdit(self)
        self.startButton = QPushButton(self.tr("Start"), self)
        self.stopButton = QPushButton(self.tr("Stop"), self)
        self.stopButton.setEnabled(False)

        self.connect(self.lineEdit, SIGNAL("returnPressed()"),
                     self.startCommand)
        self.connect(self.startButton, SIGNAL("clicked()"), self.startCommand)
        self.connect(self.stopButton, SIGNAL("clicked()"), self.stopCommand)

        layout = QGridLayout(self)
        layout.setSpacing(8)
        layout.addWidget(self.textBrowser, 0, 0, 0, 2)
        layout.addWidget(self.lineEdit, 1, 0)
        layout.addWidget(self.startButton, 1, 1)
        layout.addWidget(self.stopButton, 1, 2)

        self.process = QProcess()
        self.connect(self.process, SIGNAL("readyReadStandardOutput()"),
                     self.readOutput)
        self.connect(self.process, SIGNAL("readyReadStandardError()"),
                     self.readErrors)
        self.connect(self.process, SIGNAL("finished(int)"), self.resetButtons)

    def startCommand(self):
        args = self.lineEdit.text().split(" ")
        self.process.closeReadChannel(QProcess.StandardOutput)

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.textBrowser.clear()

        if len(args) > 1:
            self.process.start(args[0], args[1:])
        else:
            self.process.start(args[0], [])
        #print('exitCode: ' + str(self.process.exitCode()))
        #print('exitStatus: ' + str(self.process.exitStatus()))
        #print('state: ' + str(self.process.state()))
#        if self.process.exitCode() > 0:
#            self.textBrowser.setText(
#                QString("*** Failed to run %1 %2 ***").arg(
#                            self.lineEdit.text(), self.process.errorString())
#                )
#            self.startButton.setEnabled(True)
#            self.stopButton.setEnabled(False)
#            return

    def stopCommand(self):
        self.resetButtons(1)
        self.process.terminate()
        QTimer.singleShot(5000, self.process, SLOT("kill()"))

    #self.textBrowser.clear()
    def readOutput(self):
        self.textBrowser.append(QString(self.process.readAllStandardOutput()))

    def readErrors(self):
        self.textBrowser.append("error: " + QString(
                                    self.process.readAllStandardError()))

    def resetButtons(self, exitCode):
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
