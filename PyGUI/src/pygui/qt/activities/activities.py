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
    from pycore.collections import get_subdict
    from pygui.qt.utils.settings import SettingsFactory
    from pygui.qt.utils.widgets import CompositeCommon
    from pygui.qt.utils.widgets import CheckBoxCommon
    from pygui.qt.utils.widgets import LabelCommon
    from pygui.qt.utils.widgets import LineEditCommon
    from pygui.qt.utils.widgets import DockWidgetCommon
    from pygui.qt.utils.widgets import ListWidgetCommon
    from pygui.qt.utils.widgets import ListWidgetItemCommon
except ImportError as error:
    ImportErrorMessage(error, __name__)


class ActivityManager(QObject):
    @staticmethod
    def saveActivity(activity):
        SettingsFactory.saveObject(activity.activity_id, activity)

    @staticmethod
    def getActivities(activity_group):
        return SettingsFactory.getObjectsForGroup('/'.join(['activity',
                                                     activity_group]))


class ActivityWidget(CompositeCommon):
    """
    a widget used to input optional description text of activity
    """
    def __init__(self, parent, **params):
        super(ActivityWidget, self).__init__(parent, layout=QHBoxLayout(),
                                             **params)
        self.activityButton = CheckBoxCommon(self,
                            i18n="activity.button",
                            i18n_def="Save as activity",
                            clicked_handler=self.__clickedHandler__)

        LabelCommon(self,
                     i18n="activity.description.label",
                     i18n_def="Activity description (optional):")

        self.activityDescription = LineEditCommon(self, enabled=False)

    def activityOk(self):
        return self.activityButton.isChecked()

    def description(self):
        if self.activityButton.isChecked():
            return str(self.activityDescription.text())

    def __clickedHandler__(self):
        self.activityDescription.setEnabled(self.activityButton.isChecked())


class ActivityDockWidget(DockWidgetCommon):
    """
    a dock widget for activities
    """
    def __init__(self, parent, **params):
        super(ActivityDockWidget, self).__init__(parent,
                                    title=params.get('title', 'Activities'),
                                    **params)
        self.setObjectName("ActivityDockWidget")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.listWidget = ListWidgetCommon(self,
                not_add_widget_to_parent_layout=True,
                list_item_clicked_handler=self.__list_item_handler__)
        for activity in ActivityManager.getActivities(PLUGIN_ACTIVITY_TYPE):
            ListWidgetItemCommon(self.listWidget,
                                 text=activity.label,
                                 data=activity)
        self.setWidget(self.listWidget)
        parent.addDockWidget(Qt.RightDockWidgetArea, self)

    def __list_item_handler__(self, listItem):
        data = listItem.data(Qt.UserRole)
        if data:
            activity = data.toPyObject()
            if activity:
                activity()


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
