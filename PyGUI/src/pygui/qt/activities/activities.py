'''
Created on 22-01-2013

@author: jurek
'''
from pycore.special import ImportErrorMessage
try:
    import datetime
    import inspect
    from pycore.misc import replace_all
    from PyQt4.QtCore import *  # @UnusedWildImport
    from PyQt4.QtGui import *  # @UnusedWildImport
    from pycore.collections_utils import get_subdict
    from pygui.qt.utils.signals import SignalDispatcher
    from pygui.qt.utils.signals import ADD_ACTIVITY_SIGNAL
    from pygui.qt.utils.signals import CLEAR_ACTIVITIES_SIGNAL
    from pygui.qt.utils.settings import SettingsFactory
    from pygui.qt.widgets.list_widget_widget import ListWidgetWidget
    from pygui.qt.widgets.composite_widget import CompositeWidget
    from pygui.qt.widgets.check_box_widget import CheckBoxWidget
    from pygui.qt.widgets.line_edit_widget import LineEditWidget
    from pygui.qt.widgets.dock_widget_widget import DockWidgetWidget
    from pygui.qt.widgets.push_button_widget import PushButtonWidget
    from pygui.qt.widgets.label_widget import LabelWidget
    from pygui.qt.widgets.list_widget_widget import ListWidgetItemWidget
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ActivityManager(QObject):
    @staticmethod
    def saveActivity(activity):
        SettingsFactory.saveObject(activity.activity_id, activity)
        SignalDispatcher.broadcastSignal(ADD_ACTIVITY_SIGNAL, activity)

    @staticmethod
    def getActivities(activity_group=None):
        return SettingsFactory.getObjectsForGroup(
                            ActivityManager.activity_group_id(activity_group))

    @staticmethod
    def clearActivities(activity_group=None):
        SettingsFactory.clearSettings(
                            ActivityManager.activity_group_id(activity_group))

    @staticmethod
    def activity_group_id(activity_group):
        return 'activity' if activity_group == None \
                else '/'.join(['activity', activity_group])


class ActivityWidget(CompositeWidget):
    """
    a widget used to input optional description text of activity
    """
    def __init__(self, parent, **params):
        super(ActivityWidget, self).__init__(parent, layout=QHBoxLayout(),
                                             **params)
        self.activityButton = CheckBoxWidget(self,
                            i18n="activity.button",
                            i18n_def="Save as activity",
                            clicked_handler=self.__clickedHandler__)

        LabelWidget(self,
                     i18n="activity.description.label",
                     i18n_def="Activity description (optional):")

        self.activityDescription = LineEditWidget(self, enabled=False)

    def activityOk(self):
        return self.activityButton.isChecked()

    def description(self):
        if self.activityButton.isChecked():
            return str(self.activityDescription.text())

    def __clickedHandler__(self):
        self.activityDescription.setEnabled(self.activityButton.isChecked())


class ActivityDockWidget(DockWidgetWidget):
    """
    a dock widget for activities
    """
    def __init__(self, parent, **params):
        super(ActivityDockWidget, self).__init__(parent,
                                    title=params.get('title', 'Activities'),
                                    **params)
        self.setObjectName("ActivityDockWidget")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea |
                             Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        layout = QVBoxLayout()
        layout.setMargin(0)  # no margin for internal layout
        self.dockComposite = CompositeWidget(self, layout=layout,
                                        not_add_widget_to_parent_layout=True)
        self.listWidget = ListWidgetWidget(self.dockComposite,
                list_item_double_clicked_handler=self.__list_item_handler__,
                selectionMode=QAbstractItemView.MultiSelection,
                sizePolicy=QSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding))
        for activity in ActivityManager.getActivities(PLUGIN_ACTIVITY_TYPE):
            if activity:
                ListWidgetItemWidget(self.listWidget,
                                 text=activity.label,
                                 data=activity)

        self.clearAll = PushButtonWidget(self.dockComposite,
                            i18n="clear.all.activity.button",
                            i18n_def="Clear all activities",
                            clicked_handler=self.__clear_list__)

        self.setWidget(self.dockComposite)
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

        SignalDispatcher.addSignalSubscriber(self,
                                             ADD_ACTIVITY_SIGNAL,
                                             self.__add_activity__)
        SignalDispatcher.addSignalSubscriber(self,
                                             CLEAR_ACTIVITIES_SIGNAL,
                                             self.__clear_list__)

    def __list_item_handler__(self, listItem):
        data = listItem.data(Qt.UserRole)
        if data:
            activity = data.toPyObject()
            if activity:
                activity()

    def __add_activity__(self, activity):
        if activity:
            ListWidgetItemWidget(self.listWidget,
                                 text=activity.label,
                                 data=activity)

    def __clear_list__(self):
        ActivityManager.clearActivities()
        self.listWidget.clear()


PLUGIN_ACTIVITY_TYPE = 'plugin'


class Activity(object):
    def __init__(self, activity_type, **params):
        self.__activity_type__ = activity_type
        self.__params__ = params
        self.__date_time__ = datetime.datetime.now()
        self.__description__ = params.get('description', '')
        self.__activity_id__ = '/'.join(['activity', self.activity_type,
                '_'.join([self.description_as_id, self.date_and_time_as_id])])

    @property
    def params(self):
        return self.__params__

    @property
    def date_and_time_as_string(self):
        return self.__date_time__.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def date_and_time_as_id(self):
        return replace_all(self.date_and_time_as_string, '_', ['-', ' ', ':'])

    @property
    def activity_id(self):
        return self.__activity_id__

    @property
    def activity_type(self):
        return self.__activity_type__

    @property
    def label(self):
        return ' '.join([self.description, self.date_and_time_as_string])

    @property
    def description(self):
        return self.__description__

    @property
    def description_as_id(self):
        return replace_all(self.description, '_', ['-', ' ', ':', '/', ','])


class PluginActivity(Activity):
    def __init__(self, _plugin_id, **params):
        super(PluginActivity, self).__init__(PLUGIN_ACTIVITY_TYPE, **params)
        self.__plugin_id__ = _plugin_id

    @property
    def plugin_id(self):
        return self.__plugin_id__

    def __call__(self):
        #this explicit import is required here to prevent from a cyclic import
        from pygui.qt.utils.plugins import PluginsManager
        PluginsManager.invokePlugin(self.__plugin_id__, inspect.stack(),
                        **get_subdict(self.params, not_keys=['description']))
