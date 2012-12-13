'''
Created on 13-12-2012

@author: jurek
'''
from PyQt4.QtGui import *  # @UnusedWildImport
from PyQt4.QtCore import *  # @UnusedWildImport


class WidgetsHorizontalHeader(QHeaderView):
    """
    class for table header line used to create a header
    filled with widgets instead of simple texts
    widgets have to possess a layout
    """
    def __init__(self, parent, widgets):
        super(WidgetsHorizontalHeader, self).__init__(Qt.Horizontal, parent)

        #get optimal size for header line based on sizes of header widgets
        height = 0
        width = 0
        margin = 0
        for idx in range(len(widgets)):
            sizeHint = widgets[idx].sizeHint()
            if height < sizeHint.height():
                height = sizeHint.height()
            if width < sizeHint.width():
                width = sizeHint.width()
            if margin < widgets[idx].layout().margin():
                margin = widgets[idx].layout().margin()

        #very import property used in sizeHint method
        self.sizeHint = QSize(width + margin, height + margin)

        self.setResizeMode(QHeaderView.Interactive)
        parent.setHorizontalHeader(self)
        self.widgets = widgets
        for idx in range(len(self.widgets)):
            widgets[idx].setParent(self)
            x = self.sectionPosition(idx)
            y = 0
            w = widgets[idx].sizeHint().width()  # self.sectionSize(idx)
            h = height
            widgets[idx].setGeometry(QRect(x, y, w, h))

        #if a header (or section) changes then widgets have to be moved
        self.connect(self,
                     SIGNAL("sectionResized(int,int,int)"),
                     self.sectionResized)

    def sizeHint(self):
        """
        very important method without it no widgets are displayed
        """
        return self.sizeHint

    def sectionResized(self, logicalIndex, oldSize, newSize):
        """
        a section means one header
        """
        old = self.widgets[logicalIndex].geometry()
        self.widgets[logicalIndex].setGeometry(old.x(), old.y(),
                                               newSize, old.height())
        #have to move the following headers about difference
        #between old and new size
        for idx in range(logicalIndex + 1, len(self.widgets)):
            self.changeXForHeader(idx, newSize - oldSize)

    def changeXForHeader(self, logicalIndex, x):
        """
        parameter x could be positive move to right
        or negative move to left
        """
        old = self.widgets[logicalIndex].geometry()
        self.widgets[logicalIndex].setGeometry(old.x() + x, old.y(),
                                            old.width(), old.height())
