'''
Created on 13-12-2012

@author: jurek
'''
from os.path import join
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport
from pycore.misc import Params
from pygui.qt.utils.qt_i18n import QT_I18N
from pygui.qt.utils.widgets import createLabel
from pygui.qt.utils.widgets import createPlainTextEdit
from pygui.qt.utils.widgets import createPushButton


def Information(parent=None, **params):
    local_params = Params(**params)
    if local_params.title_id == None and local_params.title_default == None:
        title = "Information"
    else:
        title = QT_I18N(local_params.title_id, _default=local_params.title,
                        **params)
    information = QT_I18N(local_params.information_id,
                          _default=local_params.information,
                          **params)
    QMessageBox.information(parent, title, information)


def showFilePreviewDialog(filepath, parent=None):
    if filepath == None:
        Information(information="No files selected !")
    else:
        dialog = FilePreviewDialog(filepath, parent)
        dialog.exec_()


class FilePreviewDialog(QDialog):

    def __init__(self, filepath, parent=None):
        super(FilePreviewDialog, self).__init__(parent)
        fileparts = [str(part) for part in filepath] \
                    if hasattr(filepath, '__iter__') else [str(filepath)]
        filename = join(*fileparts)
        self.setWindowTitle('Preview of ' + filename)
        self.setGeometry(QRect(50, 50, 1000, 600))
        self.setLayout(QVBoxLayout())
        self.lineNumberLabel = createLabel(self)
        self.preview = createPlainTextEdit(self, readonly=True)

        closeButton = createPushButton(self,
                            i18n="close",
                            i18n_def="Close")
        self.connect(closeButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        file_ = QFile(filename)
        if file_.open(QFile.ReadOnly):
            self.preview.insertPlainText(QString(file_.readAll()))
            self.preview.moveCursor(QTextCursor.Start)
            self.lineNumberLabel.setText('Lines # '
                        + str(self.preview.document().lineCount()))
            file_.close()
