'''
Created on 31-10-2012

@author: jurek
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pygui.qt.utils.context import Context


class WindowTest(object):

    @staticmethod
    def show():
        parent = Context(WindowTest.show).load().parent
        if parent:
            QMessageBox.information(parent, "Show", "Hello test !")
