'''
Created on 27-09-2012

@author: jurek
'''
from hra_core.special import ImportErrorMessage
from hra_gui.qt.custom_widgets.modelviews import WidgetsHorizontalHeader
from hra_gui.qt.custom_widgets.checkable_table_header_widget import HeaderWidget
from hra_gui.qt.custom_widgets.checkable_table_header_widget import HeaderElement
from hra_core.collections_utils import create_list
import numpy as np
from hra_gui.qt.wizards.pages.choose_columns_data_page import PreviewDataViewModel
try:
    import sys
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from hra_gui.qt.widgets.table_view_widget import TableViewWidget
    #from hra_gui.qt.wizards.pages.choose_columns_data_page import PreviewDataViewModel  # @IgnorePep8
except ImportError as error:
    ImportErrorMessage(error, __name__)

__version__ = "1.0.0"


def get_model(parent, headers):
    #model = PreviewDataViewModel(parent)
    model = QStandardItemModel(parent)
    count = len(headers)
    #print(create_list("", list(range(colNumber))))
    #print(create_list("", colNumber))
    labels = QStringList(create_list("", len(headers)))
    #labels = QStringList(headers)
    #print('labels: ' + str(labels))
    model.setHorizontalHeaderLabels(labels)
    #for idx, _  in enumerate(headers):
    #    model.setHorizontalHeaderItem(idx, QStandardItem())
    #model.setColumnCount(count)
    #parent.setModel(model)
    return model


def handler(v1, v2):
    pass


__signal_header_element__ = HeaderElement('signal', 'signal', handler) # @IgnorePep8
__annotation_header_element__ = HeaderElement('annotation', 'annotation', handler) # @IgnorePep8
__time_header_element__ = HeaderElement('time', 'time', handler) # @IgnorePep8


def fill_headres(headerLine, widgetsHorizontalHeader, model, data):
    headerWidgets = []
    for num, header in enumerate(headerLine):
        widget = HeaderWidget(widgetsHorizontalHeader,
                              header,
                              [__signal_header_element__,
                               __annotation_header_element__,
                               __time_header_element__])
        headerWidgets.append(widget)
    widgetsHorizontalHeader.setWidgets(headerWidgets)

    colCount = len(headerLine)
    # create data lines
    #data = [[10, 20, 30, 40, 50], [12, 23, 34, 45, 56], [12, 23, 34, 45, 56]]
    #data = np.array([np.array([10, 20, 30, 40, 50]), np.array([12, 23, 34, 45, 56])])
    for rowData in data:
        modelData = list()
        for idx in range(colCount):
            modelData.append(QStandardItem(rowData[idx]
                                    if colCount <= len(rowData) else ""))
        model.appendRow(modelData)


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Med")
    app.setOrganizationDomain("med")
    app.setApplicationName("Custom header view")
    #app.setWindowIcon(QIcon(":/icon.png"))
    appWindow = QMainWindow(None)
    appWindow.setWindowTitle('Custom header view')

    #layout = QVBoxLayout()
    #appWindow.setLayout(layout)
    headersTablePreview = TableViewWidget(appWindow,
                            selectionBehavior=QAbstractItemView.SelectRows,
                            selectionMode=QAbstractItemView.SingleSelection,
                            not_add_widget_to_parent_layout=True)

    appWindow.setCentralWidget(headersTablePreview)
    headers = [str(el) for el in range(5)]

    #model = get_model(headersTablePreview, headers)

    model = PreviewDataViewModel(headersTablePreview)
    #model = QStandardItemModel(parent)
    count = len(headers)
    #print(create_list("", list(range(colNumber))))
    #print(create_list("", colNumber))
    labels = QStringList(create_list("", count))
    #labels = QStringList(headers)
    #print('labels: ' + str(labels))
    model.setHorizontalHeaderLabels(labels)
    headersTablePreview.setModel(model)

    widgetsHorizontalHeader = WidgetsHorizontalHeader(headersTablePreview)
    data = [[10, 20, 30, 40, 50], [12, 23, 34, 45, 56], [12, 23, 34, 45, 56]]
    #fill_headres(headers, widgetsHorizontalHeader, model, data)

    headerWidgets = []
    for num, header in enumerate(headers):
        widget = HeaderWidget(widgetsHorizontalHeader,
                              header,
                              [__signal_header_element__,
                               __annotation_header_element__,
                               __time_header_element__])
        headerWidgets.append(widget)
    widgetsHorizontalHeader.setWidgets(headerWidgets)

    colCount = len(headers)
    # create data lines
    #data = [[10, 20, 30, 40, 50], [12, 23, 34, 45, 56], [12, 23, 34, 45, 56]]
    #data = np.array([np.array([10, 20, 30, 40, 50]), np.array([12, 23, 34, 45, 56])])
    for rowData in data:
        modelData = list()
        for idx in range(colCount):
            modelData.append(QStandardItem(rowData[idx]
                                    if colCount <= len(rowData) else ""))
        model.appendRow(modelData)

    #headersTablePreview.show()
    #model.setRowCount(len(data))
    #appWindow = ApplicationMainWindow(window_title="HRA Analyzer")
    appWindow.showNormal()

    app.exec_()

main()
