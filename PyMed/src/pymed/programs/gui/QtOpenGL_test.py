'''
Created on Jul 7, 2009

@author: Stou Sandalski (stou@icapsid.net)
@license:  Public Domain
'''

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import QtGui
from PyQt4.QtOpenGL import *   # @UnusedWildImport

from test1 import test2

print(test2.Value)


class SpiralWidget(QGLWidget):
    '''
    Widget for drawing two spirals.
    '''

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(500, 500)

    def paintGL(self):
        '''
        Drawing routine
        '''

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #@UndefinedVariable @IgnorePep8
        glLoadIdentity() #@UndefinedVariable @IgnorePep8

        # Draw the spiral in 'immediate mode'
        # WARNING: You should not be doing the spiral calculation inside the
        # loop even if you are using glBegin/glEnd, sin/cos are fairly
        # expensive functions I've left it here as is to make the
        # code simpler.
        radius = 1.0
        x = radius * math.sin(0)
        y = radius * math.cos(0)
        glColor(0.0, 1.0, 0.0) #@UndefinedVariable @IgnorePep8
        glBegin(GL_LINE_STRIP) #@UndefinedVariable @IgnorePep8
        for deg in xrange(1000):
            glVertex(x, y, 0.0) #@UndefinedVariable @IgnorePep8
            rad = math.radians(deg)
            radius -= 0.001
            x = radius * math.sin(rad)
            y = radius * math.cos(rad)
        glEnd() #@UndefinedVariable @IgnorePep8

        glEnableClientState(GL_VERTEX_ARRAY) #@UndefinedVariable @IgnorePep8

        spiral_array = []

        # Second Spiral using "array immediate mode" (i.e. Vertex Arrays)
        radius = 0.8
        x = radius * math.sin(0)
        y = radius * math.cos(0)
        glColor(1.0, 0.0, 0.0) #@UndefinedVariable @IgnorePep8
        for deg in xrange(820):
            spiral_array.append([x, y])
            rad = math.radians(deg)
            radius -= 0.001
            x = radius * math.sin(rad)
            y = radius * math.cos(rad)

        glVertexPointerf(spiral_array) #@UndefinedVariable @IgnorePep8
        glDrawArrays(GL_LINE_STRIP, 0, len(spiral_array))  #@UndefinedVariable @IgnorePep8
        glFlush()  #@UndefinedVariable @IgnorePep8

    def resizeGL(self, w, h):
        '''
        Resize the GL window
        '''

        glViewport(0, 0, w, h)  #@UndefinedVariable @IgnorePep8
        glMatrixMode(GL_PROJECTION)  #@UndefinedVariable @IgnorePep8
        glLoadIdentity()  #@UndefinedVariable @IgnorePep8
        gluPerspective(40.0, 1.0, 1.0, 30.0)  #@UndefinedVariable @IgnorePep8

    def initializeGL(self):
        '''
        Initialize GL
        '''

        # set viewing projection
        glClearColor(0.0, 0.0, 0.0, 1.0)  #@UndefinedVariable @IgnorePep8
        glClearDepth(1.0) #@UndefinedVariable @IgnorePep8

        glMatrixMode(GL_PROJECTION) #@UndefinedVariable @IgnorePep8
        glLoadIdentity() #@UndefinedVariable @IgnorePep8
        gluPerspective(40.0, 1.0, 1.0, 30.0) #@UndefinedVariable @IgnorePep8


# You don't need anything below this
class SpiralWidgetDemo(QtGui.QMainWindow):
    ''' Example class for using SpiralWidget'''

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        widget = SpiralWidget(self)
        self.setCentralWidget(widget)

if __name__ == '__main__':
    app = QtGui.QApplication(['Spiral Widget Demo'])
    window = SpiralWidgetDemo()
    window.show()
    app.exec_()
