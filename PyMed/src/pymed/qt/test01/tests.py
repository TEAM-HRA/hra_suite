'''
Created on 11-12-2012

@author: jurek
'''

from PyQt4.QtCore import *  # @UnusedWildImport
from PyQt4.QtGui import *  # @UnusedWildImport
from pygui.qt.utils.widgets import createTableView
from pygui.qt.custom_widgets.modelviews import WidgetsHorizontalHeader


def createTestTable(parentLayout, parent):
    testTable = createTableView(parent,
                        selectionBehavior=QAbstractItemView.SelectRows,
                        selectionMode=QAbstractItemView.SingleSelection)
    model = QStandardItemModel(parent)

    labels = ["", "", ""]
    labels = QStringList(labels)
    model.setHorizontalHeaderLabels(labels)
    testTable.setModel(model)

    widgets = []
    for idx in range(3):
        wid = QWidget()
        widgets.append(wid)
        lay = QVBoxLayout()
        wid.setLayout(lay)
        bbb = QPushButton("BUT:" + str(idx), wid)
        lay.addWidget(bbb)
        bbb = QPushButton("EXTRA:" + str(idx), wid)
        lay.addWidget(bbb)

    hheader = WidgetsHorizontalHeader(testTable, widgets)

    for idx in range(100):
        filename = QStandardItem("jeden" + str(idx))
        size = QStandardItem('two' + str(idx))
        path = QStandardItem(str(1232132131) + str(idx))
        model.appendRow((filename, size, path, ))
