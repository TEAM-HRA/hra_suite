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

#signal emitted when a tab widget is added
TAB_WIDGET_ADDED_SIGNAL = SIGNAL("tab_widget_added()")

#signal emitted when a user click on QListWidget item
LIST_ITEM_CLICKED_SIGNAL = SIGNAL("itemClicked(QListWidgetItem *)")

#signal emitted when a user double click on QListWidget item
LIST_ITEM_DOUBLE_CLICKED_SIGNAL = SIGNAL("itemDoubleClicked(QListWidgetItem*)")

#signal emitted when there is a need to change enable state of widgets
ENABLEMEND_SIGNAL = SIGNAL('enabled_signal(bool)')


#signal emitted when tab widget is closed in by method
#pygui.qt.custom_widgets.tabwidget.TabWidgetCallableCloseHandler.__call__(self)
TAB_WIDGET_CLOSE_SIGNAL = SIGNAL('tab_widget_close_signal()')

#signal emitted when a new activity is added by
#pygui.qt.activities.activities.ActivityManager.saveActivity method
ADD_ACTIVITY_SIGNAL = SIGNAL('add_activity(PyQt_PyObject)')

#signal emitted when clear of all activities is required
CLEAR_ACTIVITIES_SIGNAL = SIGNAL('clear_activities()')

#signal emitted for example when a position changed in QComboBox widget
CURRENT_INDEX_CHANGED_SIGNAL = SIGNAL('currentIndexChanged(int)')

#signal emitted when dock widget location is changed
DOCK_WIDGET_LOCATION_CHANGED_SIGNAL = SIGNAL('dockLocationChanged(Qt::DockWidgetArea)')  # @IgnorePep8

#signal emitted when text is changing in text input widget
TEXT_CHANGED_SIGNAL = SIGNAL('textChanged(const QString&)')

#signal emitted when a button is clicked
BUTTON_CLICKED_SIGNAL = SIGNAL("buttonClicked(QAbstractButton *)")

#signal emitted for example by slider widget
VALUE_CHANGED_SIGNAL = SIGNAL("valueChanged(int)")

#signal emitted when item is check (check/uncheck) in a table view
ITEM_CHANGED_SIGNAL = SIGNAL('itemChanged(QStandardItem *)')

#signal emitted when rows are inserted into table view
ROWS_INSERTED_SIGNAL = SIGNAL('rowsInserted(const QModelIndex&,int,int)')


class SignalDispatcher(QObject):
    """
    tool class - dispatcher for custom signals,
    subscribers have to register themselves for specified signal,
    if a signal is emitted all subscribers all notify
    """

    @staticmethod
    def getDispatcher():
        return __SIGNAL_DISPATCHER__

    def __init__(self):
        super(SignalDispatcher, self).__init__()
        self.__dispatcher__ = None

    @staticmethod
    def broadcastSignal(signal, *params):
        __SIGNAL_DISPATCHER__.emitSignal(signal, *params)

    def emitSignal(self, signal, *params):
        if len(params) > 0:
            self.__dispatcher__.emit(signal, *params)
        else:
            self.__dispatcher__.emit(signal)

    @staticmethod
    def addSignalSubscriber(subscriber, signal, slot):
        __SIGNAL_DISPATCHER__.signalSubscriber(subscriber, signal, slot)

    def mainDispatcher(self, _dispatcher):
        self.__dispatcher__ = _dispatcher

    def removeSubscriber(self, subscriber):
        pass

    def signalSubscriber(self, subscriber, signal, slot):
        subscriber.connect(self.__dispatcher__, signal, slot)

    @staticmethod
    def setMainDispatcher(_dispatcher):
        __SIGNAL_DISPATCHER__.mainDispatcher(_dispatcher)

__SIGNAL_DISPATCHER__ = SignalDispatcher()
