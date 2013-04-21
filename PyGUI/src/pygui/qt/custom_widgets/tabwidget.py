'''
Created on 21-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    from PyQt4.QtGui import *  # @UnusedWildImport
    from PyQt4.QtCore import *  # @UnusedWildImport
    from pycore.misc import Params
    from pycore.misc import get_max_number_between_signs
    from pygui.qt.widgets.commons import Common
    from pygui.qt.widgets.commons import prepareWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


def close_tab_widget(tab_widget_parent, tab_widget):
    """
    method which closes specified tab
    """
    if hasattr(tab_widget, 'beforeCloseTab'):
        tab_widget.beforeCloseTab()
    idx = tab_widget_parent.indexOf(tab_widget)
    tab_widget_parent.removeTab(idx)


class TabWidgetCommon(QTabWidget, Common):
    def __init__(self, parent, **params):
        super(TabWidgetCommon, self).__init__(parent)
        prepareWidget(parent=parent, widget=self, **params)

    def closeTab(self, widget):
        close_tab_widget(self, widget)

    def tabIndex(self, object_name_or_widget):
        if isinstance(object_name_or_widget, QWidget):
            return self.indexOf(object_name_or_widget)
        else:
            for idx in range(self.count()):
                if object_name_or_widget == self.widget(idx).objectName():
                    return idx
        return -1

    def tabExists(self, object_name_or_widget):
        return self.tabIndex(object_name_or_widget) >= 0

    def setTabFocus(self, object_name_or_widget):
        if isinstance(object_name_or_widget, QWidget):
            self.setCurrentWidget(object_name_or_widget)
        else:
            self.setCurrentIndex(self.tabIndex(object_name_or_widget))

    def getNextTitle(self, title):
        titles = [_t for _t in self.getTabsTitles() if _t.startswith(title)]
        max_num = -1 if len(titles) == 0 else \
                get_max_number_between_signs(titles, from_end=True, default=0)
        return title if max_num == -1 else '%s [%d]' % (title, max_num + 1)

    def getTabsTitles(self):
        return [str(self.tabText(idx)) for idx in range(self.count())]

    def closeAllTabs(self, honour_not_close_tabs=True):
        map(self.closeTab,
                    [self.widget(idx) for idx in range(self.count())
                     if honour_not_close_tabs == False or \
                        not getattr(self.widget(idx), 'not_close', False)])

    def markTabAsNotClose(self, widget):
        """
        this method give ability to mark passed tab widget
        which can't be closed by closeAllTabs method
        """
        widget.not_close = True

    def countNotCloseTabs(self):
        """
        method which returns count of tab widget with not set 'not_close'
        property to True
        """
        return len([idx for idx in range(self.count())
                     if not getattr(self.widget(idx), 'not_close', False)])


class TabWidgetItemCommon(QWidget, Common):
    def __init__(self, **params):
        self.params = Params(**params)
        super(TabWidgetItemCommon, self).__init__(self.params.parent)
        prepareWidget(widget=self, **params)

    def closeTab(self):
        #self.params.parent has to be a QTabWidget object
        close_tab_widget(self.params.parent, self)
