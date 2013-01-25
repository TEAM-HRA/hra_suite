'''
Created on 18-01-2013

@author: jurek
'''
from pygui.qt.utils.settings import SettingsFactory
from pygui.qt.utils.settings import DEFAULT_SETTINGS_GROUP
from pygui.qt.utils.windows import AreYouSureWindow
from pygui.qt.utils.windows import InformationWindow
from pygui.qt.activities.activities import ActivityManager


def clearSettings(dargs):
    parent = dargs.get('parent', None)
    if AreYouSureWindow(parent, title='Clearing settings'):
        SettingsFactory.clearSettings(DEFAULT_SETTINGS_GROUP)
        InformationWindow(message="Settings cleared !")


def clearActivities(dargs):
    parent = dargs.get('parent', None)
    if AreYouSureWindow(parent, title='Clearing activities'):
        ActivityManager.clearActivities()
        InformationWindow(message="Activities cleared !")
