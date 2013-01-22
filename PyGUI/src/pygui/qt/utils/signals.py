'''
Created on 02-01-2013

@author: jurek
'''
from PyQt4.QtCore import *  # @UnusedWildImport

#to force call of isComplete(self) method by the Wizard framework
#which causes enable/disable state of the next button to be updated
WIZARD_COMPLETE_CHANGED_SIGNAL = SIGNAL("completeChanged()")


#the first parameter represents a name of a tab widget,
#the second represents tab widget class name in dotted (package) form,
#the third parameter is a model used in the widget
#the fourth parameter is reuse flag (true or false)
ADD_TAB_WIDGET_SIGNAL = SIGNAL("add_tab_widget(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, bool)") # @IgnorePep8


#signal emitted when a user click on QListWidget item
LIST_ITEM_CLICKED_SIGNAL = SIGNAL("itemClicked(QListWidgetItem *)")


#signal emitted when there is a need to change enable state of widgets
ENABLEMEND_SIGNAL = SIGNAL('enabled_signal(bool)')


#signal emitted when tab widget is closed in by method
#pygui.qt.custom_widgets.tabwidget.TabWidgetCallableCloseHandler.__call__(self)
TAB_WIDGET_CLOSE_SIGNAL = SIGNAL('tab_widget_close_signal()')
