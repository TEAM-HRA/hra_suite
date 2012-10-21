'''
Created on 27-09-2012

@author: jurek
'''
import sys
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from numpy import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from PyQt4 import QtGui, QtScript


def QT_test():
    def buttonInvoked():
        print('invoked !!!')

    app = QtGui.QApplication(sys.argv)

    engine = QtScript.QScriptEngine()

    button = QtGui.QPushButton()
    scriptButton = engine.newQObject(button)
    engine.globalObject().setProperty('button', scriptButton)

    engine.evaluate("button.text = 'Hello World!'")
    engine.evaluate("button.styleSheet = 'font-style: italic'")
    engine.evaluate("button.show()")

    button.connect(button, SIGNAL("clicked()"), buttonInvoked)

    sys.exit(app.exec_())


def matplotlib_test():
    numframes = 100
    numpoints = 10
    color_data = random.random((numframes, numpoints))
    x, y, c = random.random((3, numpoints))

    fig = plt.figure()
    scat = plt.scatter(x, y, c=c, s=100)

    ani = animation.FuncAnimation(fig, update_plot, frames=xrange(numframes),
                                  fargs=(color_data, scat))
    plt.show()


def update_plot(i, data, scat):
    scat.set_array(data[i])
    return scat,

matplotlib_test()
#QT_test()
