'''
Created on 27-09-2012

@author: jurek
'''
import sys
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4 import QtGui, QtScript


app = QtGui.QApplication(sys.argv)

engine = QtScript.QScriptEngine()

button = QtGui.QPushButton()
scriptButton = engine.newQObject(button)
engine.globalObject().setProperty('button', scriptButton)

engine.evaluate("button.text = 'Hello World!'")
engine.evaluate("button.styleSheet = 'font-style: italic'")
engine.evaluate("button.show()")

sys.exit(app.exec_())
