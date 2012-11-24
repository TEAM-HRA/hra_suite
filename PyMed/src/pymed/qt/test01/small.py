'''
Created on 31-10-2012

@author: jurek
'''
from PyQt4.QtGui import QMessageBox


class WindowTest(object):

    @staticmethod
    def show(dargs):
        parent = dargs.get('parent', None)
        QMessageBox.information(parent, "Test window",
            "Hello test ! (parent " + ("NOT" if parent else "IS") + " None)")
