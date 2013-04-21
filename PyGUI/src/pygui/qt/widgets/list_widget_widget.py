'''
Created on 21 kwi 2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.collections_utils import nvl
    from pygui.qt.utils.signals import LIST_ITEM_DOUBLE_CLICKED_SIGNAL
    from pygui.qt.widgets.commons import Common
    from pygui.qt.widgets.commons import prepareWidget
    from pygui.qt.widgets.commons import Common
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ListWidgetWidget(QListWidget, Common):
    def __init__(self, parent, **params):
        super(ListWidgetWidget, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)
        double_click_handler = params.get('list_item_double_clicked_handler',
                                          None)
        if double_click_handler:
            self.connect(self, LIST_ITEM_DOUBLE_CLICKED_SIGNAL,
                         double_click_handler)


class ListWidgetItemWidget(QListWidgetItem):
    def __init__(self, parent, **params):
        params = Params(**params)
        super(ListWidgetItemWidget, self).__init__(
                                            nvl(params.text, ''), parent)
        #store in data buffer of list item for later use
        if params.data:
            self.setData(Qt.UserRole, QVariant(params.data))

    def getData(self):
        item = self.data(Qt.UserRole)
        if item:
            return item.toPyObject()
